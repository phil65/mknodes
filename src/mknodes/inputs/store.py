"""The inputs store: external data resolved before rendering, pinned in a lock file."""

import asyncio
import contextlib
import dataclasses
import datetime as dt
import json
import pathlib
import threading
from typing import TYPE_CHECKING, Any, Literal

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    import os

    from mknodes.inputs.kinds import InputKind


logger = log.get_logger(__name__)

LOCK_VERSION = 1
DEFAULT_LOCK_FILE = "mknodes.lock"

# How the store treats the lock file:
# - `live`: use locked values, fetch missing ones and add them (nothing gets pruned).
# - `refresh`: fetch every used input again, the lock file keeps only the used ones.
# - `offline`: only the lock file; a missing locked input raises `MissingInputError`.
InputMode = Literal["live", "refresh", "offline"]
MODES: tuple[InputMode, ...] = ("live", "refresh", "offline")


class MissingInputError(LookupError):
    """A locked input is missing from the lock file in offline mode."""

    def __init__(self, missing: Iterable[tuple[str, str]], lock_path: pathlib.Path | None):
        self.missing = sorted(missing)
        lock = str(lock_path) if lock_path else "no lock file"
        items = "\n".join(f"  - {kind}: {key}" for kind, key in self.missing)
        msg = (
            f"{len(self.missing)} input(s) missing from the lock file ({lock}) in offline "
            f"mode:\n{items}\nBuild once without --offline to add them."
        )
        super().__init__(msg)


@dataclasses.dataclass(frozen=True)
class InputRequest:
    """A request for an external input (kind + the parameters to fetch it with)."""

    kind: str
    """Name of the input kind (see `mknodes.inputs.KINDS`)."""
    params: tuple[tuple[str, Any], ...]
    """Fetch parameters (sorted `(name, value)` pairs, values hashable)."""

    @classmethod
    def create(cls, kind: str, **params: Any) -> InputRequest:
        """Create a request, freezing list parameters to tuples."""
        frozen = {k: tuple(v) if isinstance(v, list) else v for k, v in params.items()}
        return cls(kind, tuple(sorted(frozen.items())))

    @property
    def kwargs(self) -> dict[str, Any]:
        return dict(self.params)


@dataclasses.dataclass
class InputEntry:
    """A resolved input."""

    value: Any
    """The value (JSON-serializable)."""
    fetched_at: str
    """UTC timestamp of the fetch (ISO 8601, seconds)."""
    source: str
    """Where the value came from (host / tool)."""

    def to_json(self) -> dict[str, Any]:
        return {"fetched_at": self.fetched_at, "source": self.source, "value": self.value}


def _now() -> str:
    return dt.datetime.now(dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


class InputStore:
    """Typed store of resolved external inputs (icons, licenses, LLM texts, git data, ...).

    Rendering reads inputs from the store. Values of locked kinds get pinned in a lock
    file, so builds are reproducible and can run without network access (`offline`).
    """

    def __init__(
        self,
        lock_path: str | os.PathLike[str] | None = None,
        *,
        mode: InputMode = "live",
        max_concurrency: int = 8,
    ) -> None:
        """Constructor.

        Args:
            lock_path: Lock file (read if it exists, written by `save`). None: memory only
            mode: How to treat the lock file (`live`, `refresh`, `offline`)
            max_concurrency: Maximum number of inputs fetched at the same time
        """
        if mode not in MODES:
            msg = f"Invalid inputs mode {mode!r} (one of {', '.join(MODES)})"
            raise ValueError(msg)
        self.lock_path = pathlib.Path(lock_path) if lock_path else None
        self.mode: InputMode = mode
        self.max_concurrency = max_concurrency
        self.entries: dict[tuple[str, str], InputEntry] = {}
        """(kind, key id) -> entry."""
        self.used: set[tuple[str, str]] = set()
        """Inputs read or resolved during this run."""
        self.fetched: set[tuple[str, str]] = set()
        """Inputs fetched during this run (not taken already in the store)."""
        self.on_demand: set[tuple[str, str]] = set()
        """Inputs which were fetched when read instead of in the resolve phase."""
        self._errors: dict[tuple[str, str], Exception] = {}
        self._lock = threading.Lock()
        self._loaded: dict[str, Any] = {}
        if self.lock_path and self.lock_path.is_file():
            self.load()

    def __repr__(self) -> str:
        path = str(self.lock_path) if self.lock_path else None
        return f"InputStore({path!r}, mode={self.mode!r}, n={len(self.entries)})"

    # lock file

    def load(self) -> None:
        """Read the lock file (entries of unknown kinds are kept as they are)."""
        from mknodes.inputs.kinds import KINDS

        assert self.lock_path
        data = json.loads(self.lock_path.read_text(encoding="utf-8"))
        if (version := data.get("version")) != LOCK_VERSION:
            logger.warning("Ignoring lock file %s (version %s)", self.lock_path, version)
            return
        for kind, items in data.get("inputs", {}).items():
            if kind not in KINDS:
                self._loaded[kind] = items
                continue
            for key_id, entry in items.items():
                self.entries[kind, key_id] = InputEntry(
                    value=entry["value"],
                    fetched_at=entry.get("fetched_at", ""),
                    source=entry.get("source", ""),
                )
        logger.debug("Loaded %s inputs from %s", len(self.entries), self.lock_path)

    def to_lock_data(self) -> dict[str, Any]:
        """Return the lock file content (locked kinds only)."""
        from mknodes.inputs.kinds import KINDS

        keep = self.used if self.mode == "refresh" else self.entries.keys()
        inputs: dict[str, dict[str, Any]] = {}
        if self.mode != "refresh":
            inputs |= self._loaded
        for kind, key_id in sorted(keep):
            if (entry := self.entries.get((kind, key_id))) is None or not KINDS[kind].locked:
                continue
            inputs.setdefault(kind, {})[key_id] = entry.to_json()
        return {"inputs": inputs, "version": LOCK_VERSION}

    def dumps(self) -> str:
        """Return the lock file content as deterministic JSON."""
        data = self.to_lock_data()
        return json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    def save(self) -> bool:
        """Write the lock file if its content changed (never in offline mode).

        Returns:
            Whether the file was written.
        """
        if self.lock_path is None or self.mode == "offline":
            return False
        data = self.to_lock_data()
        if not data["inputs"] and not self.lock_path.exists():
            return False
        text = json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        old = self.lock_path.read_text(encoding="utf-8") if self.lock_path.exists() else None
        if text == old:
            return False
        self.lock_path.write_text(text, encoding="utf-8")
        logger.info("Updated lock file %s", self.lock_path)
        return True

    # resolving

    def _ident(self, kind: InputKind, params: dict[str, Any]) -> tuple[str, str]:
        return kind.name, kind.key_id(params)

    def _cached(self, kind: InputKind, ident: tuple[str, str]) -> InputEntry | None:
        """Return the stored entry (raise the error of a failed fetch, or if offline)."""
        with self._lock:
            self.used.add(ident)
            if (error := self._errors.get(ident)) is not None:
                raise error
            entry = self.entries.get(ident)
            stale = self.mode == "refresh" and kind.locked and ident not in self.fetched
            if entry is not None and not stale:
                return entry
        if self.mode == "offline" and kind.locked:
            from mknodes.inputs.kinds import InputUnavailableError

            if not kind.available():
                msg = f"Input {kind.name} {ident[1]!r} is not locked and can't be fetched"
                raise InputUnavailableError(msg)
            raise MissingInputError([ident], self.lock_path)
        return None

    def _store(self, kind: InputKind, ident: tuple[str, str], value: Any) -> InputEntry:
        entry = InputEntry(value=value, fetched_at=_now(), source=kind.source)
        with self._lock:
            self.entries[ident] = entry
            self.fetched.add(ident)
        return entry

    def _missing(self, requests: Iterable[InputRequest]) -> dict[tuple[str, str], InputRequest]:
        from mknodes.inputs.kinds import get_kind

        todo: dict[tuple[str, str], InputRequest] = {}
        for request in requests:
            kind = get_kind(request.kind)
            ident = self._ident(kind, request.kwargs)
            with self._lock:
                self.used.add(ident)
                known = ident in self.entries and not (
                    self.mode == "refresh" and kind.locked and ident not in self.fetched
                )
            if not known and ident not in self._errors:
                todo.setdefault(ident, request)
        return todo

    async def resolve(self, requests: Iterable[InputRequest]) -> None:
        """Resolve the requested inputs which are not in the store yet, concurrently.

        Failed fetches get logged and remembered: reading the input raises the error.

        Raises:
            MissingInputError: Offline mode, locked inputs missing from the lock file.
        """
        from mknodes.inputs.kinds import InputUnavailableError, get_kind

        todo = self._missing(requests)
        if self.mode == "offline":
            kinds = {i: get_kind(r.kind) for i, r in todo.items()}
            missing = [i for i, k in kinds.items() if k.locked and k.available()]
            if missing:
                raise MissingInputError(missing, self.lock_path)
            todo = {i: r for i, r in todo.items() if not kinds[i].locked}
        if not todo:
            return
        logger.info("Resolving %s inputs...", len(todo))
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def fetch(ident: tuple[str, str], request: InputRequest) -> None:
            kind = get_kind(request.kind)
            async with semaphore:
                try:
                    value = await kind.fetch(request.kwargs)
                except Exception as e:  # noqa: BLE001
                    log_fn = (
                        logger.debug if isinstance(e, InputUnavailableError) else logger.warning
                    )
                    log_fn("Could not resolve input %s %r: %s", *ident, e)
                    with self._lock:
                        self._errors[ident] = e
                    return
            self._store(kind, ident, value)

        await asyncio.gather(*(fetch(i, r) for i, r in todo.items()))

    def get(self, kind: str, **params: Any) -> Any:
        """Return an input (sync). Inputs not resolved yet get fetched now.

        Raises:
            MissingInputError: Offline mode and the input is not in the lock file.
        """
        from mknodes.inputs.kinds import get_kind

        input_kind = get_kind(kind)
        ident = self._ident(input_kind, params)
        if (entry := self._cached(input_kind, ident)) is not None:
            return entry.value
        logger.debug("Fetching input %s %r on demand", *ident)
        value = input_kind.fetch_sync(params)
        self.on_demand.add(ident)
        return self._store(input_kind, ident, value).value

    async def aget(self, kind: str, **params: Any) -> Any:
        """Return an input. Inputs not resolved yet get fetched now.

        Raises:
            MissingInputError: Offline mode and the input is not in the lock file.
        """
        from mknodes.inputs.kinds import get_kind

        input_kind = get_kind(kind)
        ident = self._ident(input_kind, params)
        if (entry := self._cached(input_kind, ident)) is not None:
            return entry.value
        logger.debug("Fetching input %s %r on demand", *ident)
        value = await input_kind.fetch(params)
        self.on_demand.add(ident)
        return self._store(input_kind, ident, value).value

    def stats(self) -> dict[str, int]:
        """Return counters (used / fetched / fetched on demand / already in the store)."""
        return {
            "used": len(self.used),
            "fetched": len(self.fetched),
            "on_demand": len(self.on_demand),
            "from_store": len(self.used - self.fetched),
            "failed": len(self._errors),
        }


_active: InputStore | None = None


def active_store() -> InputStore | None:
    """Return the store of the running site build (None outside of builds).

    Used by code without a node context (themes, icon helpers, Markdown extensions).
    """
    return _active


@contextlib.contextmanager
def use_store(store: InputStore) -> Iterator[InputStore]:
    """Make given store the active one (process-wide, also for worker threads)."""
    global _active
    old, _active = _active, store
    try:
        yield store
    finally:
        _active = old

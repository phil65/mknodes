"""Build diagnostics: problems that don't stop a build but leave a page broken.

Failing `/// mknodes` blocks, `python exec="true"` blocks or nodes created in Jinja
templates render their error into the page, broken code fences and unresolved
references render as text. Each of them gets reported here: logged as a warning and
collected (with page and location) by every active `collect()` block.

Markdown extensions run inside the site engine's process. If the environment variable
`MKNODES_DIAGNOSTICS_FILE` is set (`mknodes build` does that for the engine), reports
get appended to that file as JSON lines, `load()` reads them back.

Strict mode (`mknodes build --strict`, `strict = true` in `[tool.mknodes]`) fails the
build if any diagnostic was reported (`StrictModeError`).
"""

import contextlib
import contextvars
import dataclasses
import json
import os
import pathlib
import threading
from typing import TYPE_CHECKING, Any, Literal

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Iterator


logger = log.get_logger(__name__)

FILE_ENV_VAR = "MKNODES_DIAGNOSTICS_FILE"

type DiagnosticKind = Literal["node", "mknodes-block", "exec", "fence", "reference"]

# Path of the page being rendered (used when a report doesn't name a page).
current_page: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "current_page", default=None
)

_lock = threading.Lock()
_collectors: list[list[Diagnostic]] = []


@dataclasses.dataclass(frozen=True)
class Diagnostic:
    """A problem found while building the docs."""

    kind: DiagnosticKind | str
    """What failed (`node`, `mknodes-block`, `exec`, `fence`, `reference`)."""
    message: str
    """Description of the problem (error type and message)."""
    page: str | None = None
    """Path of the page (relative to the docs dir), if known."""
    location: str | None = None
    """Where on the page (line, node, first line of the failing block)."""

    def __str__(self) -> str:
        where = self.page or "<unknown page>"
        if self.location:
            where = f"{where} ({self.location})"
        return f"{where}: [{self.kind}] {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, dct: dict[str, Any]) -> Diagnostic:
        fields = {f.name for f in dataclasses.fields(cls)}
        return cls(**{k: v for k, v in dct.items() if k in fields})


class StrictModeError(Exception):
    """Raised in strict mode if the build reported diagnostics."""

    def __init__(self, diagnostics: list[Diagnostic]) -> None:
        self.diagnostics = diagnostics
        super().__init__(summary(diagnostics))


def report(
    kind: DiagnosticKind | str,
    message: str,
    *,
    page: str | None = None,
    location: str | None = None,
) -> Diagnostic:
    """Report a problem: log a warning and add it to all active collectors.

    Args:
        kind: What failed (`node`, `mknodes-block`, `exec`, `fence`, `reference`)
        message: Description of the problem
        page: Page path (default: the page being rendered, if known)
        location: Where on the page (line, node, first line of the block)
    """
    diag = Diagnostic(kind, message, page or current_page.get(), location)
    logger.warning("%s", diag)
    with _lock:
        for collector in _collectors:
            collector.append(diag)
    if path := os.environ.get(FILE_ENV_VAR):
        try:
            with pathlib.Path(path).open("a", encoding="utf-8") as f:
                f.write(json.dumps(diag.to_dict()) + "\n")
        except OSError as e:
            logger.debug("Could not write diagnostic to %s: %s", path, e)
    return diag


@contextlib.contextmanager
def collect() -> Iterator[list[Diagnostic]]:
    """Collect all diagnostics reported inside the block (from any thread)."""
    collected: list[Diagnostic] = []
    with _lock:
        _collectors.append(collected)
    try:
        yield collected
    finally:
        with _lock:
            # By identity: collectors with equal content may be active at the same time.
            _collectors[:] = [c for c in _collectors if c is not collected]


@contextlib.contextmanager
def page_context(path: str | None) -> Iterator[None]:
    """Attribute reports without explicit page inside the block to given page."""
    token = current_page.set(path)
    try:
        yield
    finally:
        current_page.reset(token)


def load(path: str | os.PathLike[str]) -> list[Diagnostic]:
    """Read diagnostics written to a `MKNODES_DIAGNOSTICS_FILE` (missing file: none)."""
    file = pathlib.Path(path)
    if not file.is_file():
        return []
    lines = file.read_text(encoding="utf-8").splitlines()
    return [Diagnostic.from_dict(json.loads(line)) for line in lines if line.strip()]


def summary(diagnostics: list[Diagnostic]) -> str:
    """Return a summary of given diagnostics (one line each, grouped by kind)."""
    if not diagnostics:
        return "No build diagnostics"
    counts: dict[str, int] = {}
    for diag in diagnostics:
        counts[diag.kind] = counts.get(diag.kind, 0) + 1
    by_kind = ", ".join(f"{n} {kind}" for kind, n in sorted(counts.items()))
    lines = [f"{len(diagnostics)} build diagnostics ({by_kind}):"]
    lines += [f"  {diag}" for diag in diagnostics]
    return "\n".join(lines)


def page_of(md: Any) -> str | None:
    """Return the path of the page a Python-Markdown instance renders, if known.

    Zensical registers a `rendering_context` preprocessor holding the page; other
    engines don't expose it (then the page being rendered by mknodes is used, if any).
    """
    try:
        if "rendering_context" in md.preprocessors:
            return str(md.preprocessors["rendering_context"].page.path)
    except AttributeError, KeyError, TypeError:
        pass
    return current_page.get()


def describe_exception(exc: BaseException) -> str:
    """Return `Type: message` of given exception and of its causes (wrapped Jinja errors)."""
    parts: list[str] = []
    seen: set[int] = set()
    current: BaseException | None = exc
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        text = " ".join(str(current).split())
        parts.append(f"{type(current).__name__}: {text}" if text else type(current).__name__)
        current = current.__cause__
    return " <- ".join(parts)


def node_page(node: Any) -> str | None:
    """Return the file path of the page containing given node (None if unknown)."""
    import mknodes as mk

    page = node if isinstance(node, mk.MkPage) else getattr(node, "parent_page", None)
    try:
        return pathlib.PurePath(page.resolved_file_path).as_posix() if page else None
    except Exception:  # noqa: BLE001
        return None


def first_line(text: str, max_len: int = 80) -> str:
    """Return the first non-empty line of given text (shortened), for locations."""
    line = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    return line if len(line) <= max_len else f"{line[: max_len - 3]}..."

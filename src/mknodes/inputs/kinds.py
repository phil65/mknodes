"""Input kinds: how a kind of external input gets identified and fetched."""

from __future__ import annotations

import asyncio
import hashlib
import json
from typing import Any, ClassVar
import urllib.parse

from mknodes.utils import coroutines


class InputUnavailableError(RuntimeError):
    """An input can't be fetched in this environment (missing extra, no API key, ...)."""


def _canonical(params: dict[str, Any]) -> str:
    return json.dumps(params, sort_keys=True, separators=(",", ":"), default=str)


class InputKind:
    """A kind of external input (icons, licenses, LLM texts, ...).

    Subclasses define `name`, `source`, `fetch` and optionally `key_id` / `fetch_sync`.
    """

    name: ClassVar[str]
    """Namespace in the store and in the lock file."""
    source: ClassVar[str] = ""
    """Where values come from (written to the lock file)."""
    locked: ClassVar[bool] = True
    """Whether values get pinned in the lock file.

    Unlocked kinds are local and deterministic for a checkout / environment (git, the
    installed packages): resolved every build, also in offline mode.
    """

    def available(self) -> bool:
        """Whether inputs of this kind can be fetched here (e.g. an optional extra).

        Offline, a missing input of an unavailable kind raises `InputUnavailableError`
        (the node may use a placeholder) instead of `MissingInputError`.
        """
        return True

    def key_id(self, params: dict[str, Any]) -> str:
        """Return the id of the input (key in the lock file)."""
        return _canonical({k: v for k, v in params.items() if v is not None})

    async def fetch(self, params: dict[str, Any]) -> Any:
        """Fetch the value (JSON-serializable)."""
        raise NotImplementedError

    def fetch_sync(self, params: dict[str, Any]) -> Any:
        """Fetch the value from sync code."""
        return coroutines.run_sync(self.fetch(params))

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name!r})"


class IconInput(InputKind):
    """Icon SVGs from the Iconify API (params: `icon` + SVG params of `get_icon_svg`).

    Fetches go through the on-disk icon cache (`mknodes.utils.iconcache`).
    """

    name = "icon"
    source = "api.iconify.design"

    def key_id(self, params: dict[str, Any]) -> str:
        icon = params["icon"]
        rest = {
            k: str(v) for k, v in sorted(params.items()) if k != "icon" and v not in (None, False)
        }
        return f"{icon}?{urllib.parse.urlencode(rest)}" if rest else icon

    async def fetch(self, params: dict[str, Any]) -> str:
        from mknodes.utils import iconcache

        return await iconcache.fetch_icon_svg_async(**params)

    def fetch_sync(self, params: dict[str, Any]) -> str:
        from mknodes.utils import iconcache

        return iconcache.fetch_icon_svg(**params)


class LicenseInput(InputKind):
    """License texts from the SPDX license list (params: `name`, an SPDX id or name)."""

    name = "license"
    source = "spdx.org"

    def key_id(self, params: dict[str, Any]) -> str:
        return params["name"].lower()

    async def fetch(self, params: dict[str, Any]) -> dict[str, Any]:
        import dataclasses

        from mknodes.info import license as lic

        obj = await lic.License.from_name(params["name"])
        return dataclasses.asdict(obj)


class LlmInput(InputKind):
    """LLM completions (params: `user_prompt`, `system_prompt`, `model`, `context`).

    The key is a hash of all params: the prompts and the context can be long.
    """

    name = "llm"
    source = "agentpool"

    def key_id(self, params: dict[str, Any]) -> str:
        digest = hashlib.sha256(_canonical(params).encode()).hexdigest()[:24]
        return f"{params.get('model')}:{digest}"

    def available(self) -> bool:
        try:
            import agentpool.functional  # noqa: F401
        except ImportError:  # optional extra (`mknodes[llm]`), missing or broken
            return False
        return True

    async def fetch(self, params: dict[str, Any]) -> str:
        from mknodes.templatenodes.mkllm import complete_llm

        if not self.available():
            msg = "agentpool unavailable (install `mknodes[llm]`)"
            raise InputUnavailableError(msg)

        return await complete_llm(**params)


class ChangelogInput(InputKind):
    """A changelog built from the git history (params: see `mkchangelog.get_changelog`)."""

    name = "changelog"
    source = "git-changelog"
    locked = False

    async def fetch(self, params: dict[str, Any]) -> str:
        from mknodes.templatenodes.mkchangelog import get_changelog

        return await asyncio.to_thread(get_changelog, **params)

    def fetch_sync(self, params: dict[str, Any]) -> str:
        from mknodes.templatenodes.mkchangelog import get_changelog

        return get_changelog(**params)


class PipDepTreeInput(InputKind):
    """Mermaid code of the dependency tree of an installed package (`pipdeptree`)."""

    name = "pipdeptree"
    source = "pipdeptree"
    locked = False

    async def fetch(self, params: dict[str, Any]) -> str:
        from mknodes.templatenodes.mkpipdeptree import get_mermaid

        return await asyncio.to_thread(get_mermaid, **params)

    def fetch_sync(self, params: dict[str, Any]) -> str:
        from mknodes.templatenodes.mkpipdeptree import get_mermaid

        return get_mermaid(**params)


# Registered input kinds by name.
KINDS: dict[str, InputKind] = {}


def register_kind(kind: InputKind) -> InputKind:
    """Register an input kind (replaces a kind with the same name)."""
    KINDS[kind.name] = kind
    return kind


def get_kind(name: str) -> InputKind:
    """Return the input kind with given name."""
    try:
        return KINDS[name]
    except KeyError:
        msg = f"Unknown input kind {name!r} (known: {', '.join(sorted(KINDS))})"
        raise KeyError(msg) from None


for _kind in (IconInput(), LicenseInput(), LlmInput(), ChangelogInput(), PipDepTreeInput()):
    register_kind(_kind)

"""Persistent on-disk cache for icon SVGs fetched from the Iconify API.

Icons are immutable per name, so cached SVGs never expire. Every docs build
otherwise fetches its icons from api.iconify.design, which rate-limits shared
CI runners (HTTP 429).

The cache lives in ``$MKNODES_CACHE_DIR/icons`` if the ``MKNODES_CACHE_DIR``
environment variable is set, otherwise in the platform's user cache directory
(e.g. ``~/.cache/mknodes/icons`` on Linux). Use [clear_icon_cache][] to empty it.

Lookups are resolved without network access, so a build with all icons cached
works offline. Icons are fetched correctly from sync code as well as from inside a
running event loop; async code should use [get_icon_svg_async][] (it does not block
the loop). During a site build, [get_icon_svg][] reads from the active inputs store
(`mknodes.inputs`, lock file), which fetches via [fetch_icon_svg][].
"""

import asyncio
import contextvars
import functools
import hashlib
import os
import pathlib
import shutil
import tempfile
from typing import TYPE_CHECKING, Any

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Sequence

    from jinjarope.iconfilters import Flip, Rotation


logger = log.get_logger(__name__)

CACHE_DIR_ENV_VAR = "MKNODES_CACHE_DIR"
_UNRESOLVED = "_"
_memory_cache: dict[pathlib.Path, str] = {}


def get_cache_dir() -> pathlib.Path:
    """Return the directory where icon SVGs are cached."""
    if root := os.environ.get(CACHE_DIR_ENV_VAR):
        return pathlib.Path(root).expanduser() / "icons"
    import platformdirs

    return pathlib.Path(platformdirs.user_cache_dir("mknodes", appauthor=False)) / "icons"


def clear_icon_cache() -> None:
    """Remove all cached icons (on disk and in memory)."""
    _memory_cache.clear()
    shutil.rmtree(get_cache_dir(), ignore_errors=True)


def _local_key(icon: str) -> str:
    """Normalize an icon spec to "prefix:name" as far as possible without network access.

    Mirrors jinjarope's ``get_pyconify_key``, minus the lookup of icon set prefixes
    in the Iconify collection list. Specs which need that lookup (like
    ":fa-brands-github:") are returned as normalized spec without a colon.
    """
    from jinjarope import icons

    for k, v in icons.PYCONIFY_TO_PREFIXES.items():
        path = f"{v.replace('-', '/')}/"
        icon = icon.replace(path, f"{k}:")
        icon = icon.replace(f":{v}-", f"{k}:")
    icon = icon.strip().strip(":")
    if (count := icon.count(":")) > 1:
        icon = icon.replace(":", "-", count - 1)
    return icon


def _params_suffix(params: dict[str, Any]) -> str:
    used = {k: str(v) for k, v in sorted(params.items()) if v is not None and v is not False}
    if not used:
        return ""
    digest = hashlib.sha256(repr(sorted(used.items())).encode()).hexdigest()[:16]
    return f"--{digest}"


def _safe(part: str) -> str:
    return "".join(c if c.isalnum() or c in "-_." else "_" for c in part) or "_"


def get_cache_path(icon: str, **params: Any) -> pathlib.Path:
    """Return the cache file path for a single icon spec and SVG parameters.

    Args:
        icon: Icon spec (e.g. "mdi:file", "material/file", ":material-file:")
        params: SVG parameters (color, height, width, flip, rotate, box)
    """
    key = _local_key(icon)
    folder, name = key.split(":", 1) if ":" in key else (_UNRESOLVED, key)
    return get_cache_dir() / _safe(folder) / f"{_safe(name)}{_params_suffix(params)}.svg"


def _is_svg(text: str) -> bool:
    return text.lstrip().startswith("<svg") and text.rstrip().endswith("</svg>")


def _read(path: pathlib.Path) -> str | None:
    if (cached := _memory_cache.get(path)) is not None:
        return cached
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return None
    if not _is_svg(text):
        logger.debug("Ignoring invalid cached icon %s", path)
        return None
    _memory_cache[path] = text
    return text


def _write(path: pathlib.Path, text: str) -> None:
    _memory_cache[path] = text
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write atomically, parallel builds may store the same icon.
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(text)
        pathlib.Path(tmp).replace(path)
    except OSError as e:
        logger.debug("Could not cache icon at %s: %s", path, e)


def fetch_icon_prefixes() -> list[str]:
    """Return the prefixes of all Iconify icon sets (network, anyenv HTTP cache).

    Runs in an empty context, like [fetch_icon_svg][mknodes.utils.iconcache.fetch_icon_svg]
    (pycons' sync bridge fails inside a running event loop otherwise).
    """
    from jinjarope import icons

    return sorted(contextvars.Context().run(icons._get_collection_map))


@functools.cache
def _fetch_icon_prefixes_cached() -> tuple[str, ...]:
    return tuple(fetch_icon_prefixes())


def get_icon_prefixes() -> Sequence[str]:
    """Return the prefixes of all Iconify icon sets.

    During a site build they come from the active inputs store (kind `icon_prefixes`,
    pinned in the lock file), otherwise they get fetched once per process.
    """
    from mknodes import inputs

    if (store := inputs.active_store()) is not None:
        return store.get("icon_prefixes")
    return _fetch_icon_prefixes_cached()


def get_pyconify_key(icon: str) -> str:
    """Convert an icon spec to a pyconify key ("prefix:name").

    Like jinjarope's ``get_pyconify_key``, but the list of icon sets is only needed
    (and read from the inputs store during builds) for specs without a prefix
    separator, like ":fa-brands-github:". The longest matching icon set prefix wins,
    specs without a known prefix fall back to "mdi".

    Args:
        icon: Icon spec ("mdi:file", "material/file", ":material-file:", "fa-brands-github")
    """
    key = _local_key(icon)
    if ":" in key:
        return key
    for prefix in sorted(get_icon_prefixes(), key=len, reverse=True):
        if key.startswith(f"{prefix}-"):
            return f"{prefix}:{key.removeprefix(f'{prefix}-')}"
    return f"mdi:{key}"


def _fetch_unisolated(icon: str, **params: Any) -> str:
    from pycons.iconify import api

    return api.svg(get_pyconify_key(icon), **params).decode()


def _fetch(icon: str, **params: Any) -> str:
    """Fetch an icon from the Iconify API (blocking).

    pycons fetches via anyenv's sync bridge, which runs the request in a new event
    loop (in a helper thread if the current thread already runs one). The bridge copies
    the current context, which inside a running loop carries anyio's / sniffio's
    "current async library" marker, so the helper thread refuses to start its loop and
    the request coroutine never gets awaited. Running in an empty context avoids that.
    """
    return contextvars.Context().run(_fetch_unisolated, icon, **params)


def _get_cached(spec: str, params: dict[str, Any]) -> tuple[pathlib.Path, str | None]:
    path = get_cache_path(spec, **params)
    return path, _read(path)


def _store(path: pathlib.Path, svg: str) -> None:
    if _is_svg(svg):
        _write(path, svg)


async def fetch_icon_svg_async(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Async version of [fetch_icon_svg][mknodes.utils.iconcache.fetch_icon_svg].

    Icons missing from the cache are fetched in a worker thread, so the event loop
    keeps running.

    Args:
        icon: Icon spec(s)
        color: Icon color. Replaces currentColor with specific color.
        height: Icon height
        width: Icon width
        flip: Flip icon
        rotate: Rotate icon. If an integer is provided, it is assumed to be in degrees.
        box: Add an empty rectangle matching the icon's viewBox
    """
    params: dict[str, Any] = dict(
        color=color, height=height, width=width, flip=flip, rotate=rotate, box=box
    )
    label = ""
    for spec in icon.split("|"):
        path, svg = _get_cached(spec, params)
        if svg is None:
            svg = await asyncio.to_thread(_fetch, spec, **params)
            _store(path, svg)
        label += svg
    return label


def fetch_icon_svg(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Return svg for given icon, using the on-disk icon cache (not the inputs store).

    Drop-in replacement for ``jinjarope.iconfilters.get_icon_svg``: accepts the same
    icon specs ("mdi:file", "material/file", ":material-file:", "file") and
    "|"-separated lists of them. Only icons missing from the cache are fetched.

    Args:
        icon: Icon spec(s)
        color: Icon color. Replaces currentColor with specific color.
        height: Icon height
        width: Icon width
        flip: Flip icon
        rotate: Rotate icon. If an integer is provided, it is assumed to be in degrees.
        box: Add an empty rectangle matching the icon's viewBox
    """
    params: dict[str, Any] = dict(
        color=color, height=height, width=width, flip=flip, rotate=rotate, box=box
    )
    label = ""
    for spec in icon.split("|"):
        path, svg = _get_cached(spec, params)
        if svg is None:
            svg = _fetch(spec, **params)
            _store(path, svg)
        label += svg
    return label


def get_icon_svg(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Return svg for given icon.

    During a site build the icon comes from the active inputs store (lock file, see
    `mknodes.inputs`), otherwise from [fetch_icon_svg][mknodes.utils.iconcache.fetch_icon_svg]
    (on-disk cache, fetched if missing).

    Args:
        icon: Icon spec(s) ("mdi:file", "material/file", ":material-file:", "a|b")
        color: Icon color. Replaces currentColor with specific color.
        height: Icon height
        width: Icon width
        flip: Flip icon
        rotate: Rotate icon. If an integer is provided, it is assumed to be in degrees.
        box: Add an empty rectangle matching the icon's viewBox
    """
    from mknodes import inputs

    params: dict[str, Any] = dict(
        color=color, height=height, width=width, flip=flip, rotate=rotate, box=box
    )
    if (store := inputs.active_store()) is not None:
        return store.get("icon", icon=icon, **params)
    return fetch_icon_svg(icon, **params)


async def get_icon_svg_async(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Async version of [get_icon_svg][mknodes.utils.iconcache.get_icon_svg].

    Args:
        icon: Icon spec(s) ("mdi:file", "material/file", ":material-file:", "a|b")
        color: Icon color. Replaces currentColor with specific color.
        height: Icon height
        width: Icon width
        flip: Flip icon
        rotate: Rotate icon. If an integer is provided, it is assumed to be in degrees.
        box: Add an empty rectangle matching the icon's viewBox
    """
    from mknodes import inputs

    params: dict[str, Any] = dict(
        color=color, height=height, width=width, flip=flip, rotate=rotate, box=box
    )
    if (store := inputs.active_store()) is not None:
        return await store.aget("icon", icon=icon, **params)
    return await fetch_icon_svg_async(icon, **params)

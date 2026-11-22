"""Persistent on-disk cache for icon SVGs fetched from the Iconify API.

Icons are immutable per name, so cached SVGs never expire. Every docs build
otherwise fetches its icons from api.iconify.design, which rate-limits shared
CI runners (HTTP 429).

The cache lives in ``$MKNODES_CACHE_DIR/icons`` if the ``MKNODES_CACHE_DIR``
environment variable is set, otherwise in the platform's user cache directory
(e.g. ``~/.cache/mknodes/icons`` on Linux). Use [clear_icon_cache][] to empty it.

Lookups are resolved without network access, so a build with all icons cached
works offline.
"""

from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import tempfile
from typing import TYPE_CHECKING, Any

from mknodes.utils import log


if TYPE_CHECKING:
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


def _fetch(icon: str, **params: Any) -> str:
    from jinjarope import iconfilters
    from pycons.iconify import api

    key = iconfilters.get_pyconify_key(icon)
    return api.svg(key, **params).decode()


def get_icon_svg(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Return svg for given icon, using the on-disk icon cache.

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
        path = get_cache_path(spec, **params)
        if (svg := _read(path)) is None:
            svg = _fetch(spec, **params)
            if _is_svg(svg):
                _write(path, svg)
        label += svg
    return label

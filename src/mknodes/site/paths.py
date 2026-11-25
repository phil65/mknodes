"""Path constants of the site generator."""

from __future__ import annotations

from mknodes import paths


RESOURCES = paths.RESOURCES / "site"
CFG_DEFAULT = "mkdocs.yml"
DEFAULT_BUILD_FN = "mknodes.site:parse"

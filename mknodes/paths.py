"""Filesystem paths."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).parent

TEST_RESOURCES = ROOT.parent / "tests" / "data"
RESOURCES = ROOT / "resources"

DEFAULT_BUILD_FN = "mknodes:MkDefaultWebsite.for_project"

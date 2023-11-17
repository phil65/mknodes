"""Filesystem paths."""

from __future__ import annotations

import pathlib


ROOT = pathlib.Path(__file__).parent

TEST_RESOURCES = ROOT.parent / "tests" / "data"
RESOURCES = ROOT / "resources"

DEFAULT_BUILD_FN = "mknodes.navs.mkemptywebsite:MkEmptyWebsite.for_project"

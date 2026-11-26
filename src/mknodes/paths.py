"""Filesystem paths."""

import pathlib


ROOT = pathlib.Path(__file__).parent

TEST_RESOURCES = ROOT.parent.parent / "tests" / "data"
RESOURCES = ROOT / "resources"

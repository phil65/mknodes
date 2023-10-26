from __future__ import annotations

import pathlib

import pytest

import mknodes as mk

from mknodes.manual import root


@pytest.fixture(scope="session")
def test_data_dir():
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def resources_dir():
    return pathlib.Path(__file__).parent.parent / "mknodes/resources/"


@pytest.fixture(scope="session")
def mknodes_project():
    theme = mk.MaterialTheme()
    proj = mk.Project(theme=theme)
    root.build(proj)
    return proj

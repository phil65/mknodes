from __future__ import annotations

import pathlib

import pytest

import mknodes

from mknodes import manual, project


@pytest.fixture(scope="session")
def test_data_dir():
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def resources_dir():
    return pathlib.Path(__file__).parent.parent / "mknodes/resources/"


@pytest.fixture(scope="session")
def full_tree():
    proj = project.Project(mknodes)
    return manual.create_root(proj)

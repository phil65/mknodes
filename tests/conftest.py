from __future__ import annotations

import pathlib

from mkdocs import config
import pytest

from mknodes import manual


@pytest.fixture(scope="session")
def test_data_dir():
    return pathlib.Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def resources_dir():
    return pathlib.Path(__file__).parent.parent / "mknodes/resources/"


@pytest.fixture(scope="session")
def full_tree():
    cfg = config.load_config("mkdocs.yml")
    return manual.create_root(cfg)

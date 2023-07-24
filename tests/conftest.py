from __future__ import annotations

import pathlib

import pytest


@pytest.fixture(scope="session")
def test_data_dir():
    return pathlib.Path(__file__).parent / "data"

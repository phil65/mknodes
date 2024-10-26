from __future__ import annotations

import pytest

from mknodes.utils import pathhelpers


def test_finding_pyproject():
    path = pathhelpers.find_cfg_for_folder("pyproject.toml", ".")
    assert path


def test_finding_nonexisting():
    path = pathhelpers.find_cfg_for_folder("i-dont-exist.toml", ".")
    assert not path


if __name__ == "__main__":
    pytest.main([__file__])

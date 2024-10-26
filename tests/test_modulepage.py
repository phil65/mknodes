from __future__ import annotations

import pytest

import mknodes as mk


def test_modulepage():
    mk.MkModulePage(mk)


if __name__ == "__main__":
    pytest.main([__file__])

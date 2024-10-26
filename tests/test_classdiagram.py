from __future__ import annotations

import pytest

import mknodes as mk


def test_modes():
    mk.MkClassDiagram(mk.MkClassDiagram, mode="mro")
    mk.MkClassDiagram(mk.MkClassDiagram, mode="subclasses")
    mk.MkClassDiagram(mk.MkClassDiagram, mode="baseclasses")


if __name__ == "__main__":
    pytest.main([__file__])

from __future__ import annotations

import mknodes


def test_modes():
    mknodes.MkClassDiagram(mknodes.MkClassDiagram, mode="mro")
    mknodes.MkClassDiagram(mknodes.MkClassDiagram, mode="subclass_tree")
    mknodes.MkClassDiagram(mknodes.MkClassDiagram, mode="parent_tree")

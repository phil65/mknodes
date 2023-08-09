from __future__ import annotations

import mknodes


def test_modes():
    mknodes.MkClassDiagram(mknodes.MkClassDiagram, mode="mro")
    mknodes.MkClassDiagram(mknodes.MkClassDiagram, mode="subclasses")
    mknodes.MkClassDiagram(mknodes.MkClassDiagram, mode="baseclasses")

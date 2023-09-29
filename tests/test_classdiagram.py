from __future__ import annotations

import mknodes as mk


def test_modes():
    mk.MkClassDiagram(mk.MkClassDiagram, mode="mro")
    mk.MkClassDiagram(mk.MkClassDiagram, mode="subclasses")
    mk.MkClassDiagram(mk.MkClassDiagram, mode="baseclasses")

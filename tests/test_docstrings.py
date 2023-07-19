from __future__ import annotations

import mknodes


def test_docstrings():
    docstrings = mknodes.MkDocStrings(obj=mknodes)
    assert str(docstrings) == "::: mknodes\n"

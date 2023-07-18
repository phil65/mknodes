from __future__ import annotations

import mknodes


def test_docstrings():
    docstrings = mknodes.DocStrings(obj=mknodes)
    assert str(docstrings) == "::: mknodes\n"

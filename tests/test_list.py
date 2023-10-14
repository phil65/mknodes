from __future__ import annotations

import mknodes as mk


EXPECTED = """## test

  * a
  * b
"""


def test_list():
    ls = mk.MkList()
    assert not str(ls)


def test_markdown():
    ls = mk.MkList(["a", "b"], header="test")
    assert str(ls) == EXPECTED

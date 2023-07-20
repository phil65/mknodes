from __future__ import annotations

import mknodes


EXPECTED = """## test

  * a
  * b
"""


def test_list():
    ls = mknodes.MkList()
    assert not str(ls)


def test_markdown():
    ls = mknodes.MkList(["a", "b"], header="test")
    assert str(ls) == EXPECTED

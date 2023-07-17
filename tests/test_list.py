from __future__ import annotations

import markdownizer


EXPECTED = """## test

  - a
  - b
"""


def test_list():
    ls = markdownizer.List()
    assert not str(ls)


def test_markdown():
    ls = markdownizer.List(["a", "b"], header="test")
    assert str(ls) == EXPECTED

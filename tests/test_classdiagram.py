from __future__ import annotations

import mknodes


EXPECTED = """!!! info
    This is a test
"""


def test_admonition():
    ls = mknodes.MkAdmonition("")
    assert not str(ls)


def test_markdown():
    ls = mknodes.MkAdmonition("This is a test")
    assert str(ls) == EXPECTED

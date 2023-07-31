from __future__ import annotations

import mknodes


EXPECTED = """/// tab | abc
    new: True

bcd
///
"""

NESTED_EXPECTED = """/// outer

//// inner_1

inner_1 content
////


//// inner_2

inner_2 content
////
///
"""


def test_block():
    node = mknodes.MkBlock(
        "tab",
        argument="abc",
        content="bcd",
        attributes=dict(new=True),
    )
    assert str(node) == EXPECTED


def test_nested_block():
    inner_1 = mknodes.MkBlock("inner_1", content="inner_1 content")
    inner_2 = mknodes.MkBlock("inner_2", content="inner_2 content")
    outer = mknodes.MkBlock("outer", content=[inner_1, inner_2])
    assert str(outer) == NESTED_EXPECTED

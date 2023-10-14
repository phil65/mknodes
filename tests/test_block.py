from __future__ import annotations

import mknodes as mk


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
    node = mk.MkBlock(
        "tab",
        argument="abc",
        content="bcd",
        attributes=dict(new=True),
    )
    assert str(node) == EXPECTED


def test_nested_block():
    inner_1 = mk.MkBlock("inner_1", content="inner_1 content")
    inner_2 = mk.MkBlock("inner_2", content="inner_2 content")
    outer = mk.MkBlock("outer", content=[inner_1, inner_2])
    assert str(outer) == NESTED_EXPECTED

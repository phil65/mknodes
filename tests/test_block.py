from __future__ import annotations

import mknodes


EXPECTED = """/// tab | abc
    new: True
bcd
///
"""


def test_block():
    node = mknodes.MkBlock("tab", title="abc", content="bcd", attributes=dict(new=True))
    assert str(node) == EXPECTED

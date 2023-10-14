from __future__ import annotations

import mknodes as mk


EXPECTED = """/// tab | Tab1
    new: True

Some text
///

/// tab | Tab2

Another text
///
"""


def test_tabblock():
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = mk.MkTabbedBlocks(tabs)
    assert str(tabblock) == EXPECTED

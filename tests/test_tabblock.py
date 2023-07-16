from __future__ import annotations

import markdownizer


EXPECTED = """/// tab | Tab1
Some text
///

/// tab | Tab2
Another text
///

"""


def test_list():
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = markdownizer.TabBlock(tabs)
    assert str(tabblock) == EXPECTED

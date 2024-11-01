from __future__ import annotations

import pytest

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
    """Test the creation and string representation of a tabbed block.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the tabbed block does not match the expected output.
    """
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = mk.MkTabbedBlocks(tabs)
    assert str(tabblock) == EXPECTED


if __name__ == "__main__":
    pytest.main([__file__])

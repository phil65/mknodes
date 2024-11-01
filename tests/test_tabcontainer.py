from __future__ import annotations

import pytest

import mknodes as mk


EXPECTED_TABBED = """===! "Tab1"
    Some text

=== "Tab2"
    Another text
"""


def test_mktabbed():
    """Test the creation and functionality of a MkTabbed object.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If any of the assertions fail during the test.
    """
    tabs = dict(Tab1="Some text", Tab2="Another text")
    node = mk.MkTabbed(tabs)
    assert len(node.items) == 2  # noqa: PLR2004
    # assert str(node["Tab1"]) == "Some text"
    # assert str(node[1]) == "Another text"
    assert str(node) == EXPECTED_TABBED
    node["Tab3"] = "And another one"


if __name__ == "__main__":
    pytest.main([__file__])

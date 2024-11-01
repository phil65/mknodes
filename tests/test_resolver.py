from __future__ import annotations

import pytest

import mknodes as mk
from mknodes.treelib import noderesolver


def test_resolver():
    """Tests the functionality of the MkNodeResolver class.
    
    This method creates a MkNodeResolver instance, constructs a simple navigation
    structure using MkNav, and tests the glob method of the resolver.
    
    Returns:
        None: This method doesn't return anything explicitly. It uses an assert
        statement to verify the expected behavior.
    
    Raises:
        AssertionError: If the glob method doesn't return the expected result.
    """
    resolver = noderesolver.MkNodeResolver()
    root = mk.MkNav()
    sub = root.add_nav("SubNav")
    page = sub.add_page("Test")
    page += mk.MkAdmonition("Test")
    result = resolver.glob("*/*/MkAdm*", root)
    assert result


if __name__ == "__main__":
    pytest.main([__file__])

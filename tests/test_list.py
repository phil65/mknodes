from __future__ import annotations

import pytest

import mknodes as mk


EXPECTED = """## test

  * a
  * b
"""


def test_list():
    """Test the creation of an empty MkList.
    
    This method creates an instance of MkList and asserts that its string
    representation is empty, verifying the initial state of a newly created list.
    
    Args:
        None
    
    Returns:
        None: This method doesn't return anything explicitly.
    
    Raises:
        AssertionError: If the string representation of the newly created MkList
                        is not empty.
    """
    ls = mk.MkList()
    assert not str(ls)


def test_markdown():
    """Test the markdown list generation functionality.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the generated markdown list does not match the expected output.
    """
    ls = mk.MkList(["a", "b"], header="test")
    assert str(ls) == EXPECTED


if __name__ == "__main__":
    pytest.main([__file__])

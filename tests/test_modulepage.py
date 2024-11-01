from __future__ import annotations

import pytest

import mknodes as mk


def test_modulepage():
    """Test the creation of a module page.
    
    This function tests the functionality of the MkModulePage class from the mk module.
    It creates an instance of MkModulePage with the mk module as an argument.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        Any exceptions raised by MkModulePage constructor are not caught and will propagate.
    """
    mk.MkModulePage(mk)


if __name__ == "__main__":
    pytest.main([__file__])

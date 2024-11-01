from __future__ import annotations

import pytest

from mknodes.utils import pathhelpers


def test_finding_pyproject():
    """Test finding pyproject.toml file in the current directory.
    
    This method tests the functionality of finding a pyproject.toml configuration file
    in the current directory using the pathhelpers.find_cfg_for_folder function.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the pyproject.toml file is not found in the current directory.
    """
    path = pathhelpers.find_cfg_for_folder("pyproject.toml", ".")
    assert path


def test_finding_nonexisting():
    """Tests finding a non-existing configuration file.
    
    This method tests the behavior of the `find_cfg_for_folder` function when 
    attempting to locate a configuration file that does not exist.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the `find_cfg_for_folder` function returns a path 
                        for a non-existing file.
    """
    path = pathhelpers.find_cfg_for_folder("i-dont-exist.toml", ".")
    assert not path


if __name__ == "__main__":
    pytest.main([__file__])

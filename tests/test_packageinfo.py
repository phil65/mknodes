from __future__ import annotations

import pytest

from mknodes.info import packageregistry


def test_packageinfo():
    """Tests the package information retrieval for the 'mknodes' package.
    
    This method verifies that the package information for 'mknodes' is correctly
    retrieved and contains the expected data. It also checks that information
    for all required packages can be obtained.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If any of the assertions fail, indicating unexpected
                        package information or inability to retrieve required
                        package information.
    """
    info = packageregistry.get_info("mknodes")
    assert info.license_name == "MIT"
    assert info.keywords
    assert info.extras is not None
    for package in info.required_package_names:
        packageregistry.get_info(package)


if __name__ == "__main__":
    pytest.main([__file__])

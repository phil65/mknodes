from __future__ import annotations

from mknodes.info import packageregistry


def test_packageinfo():
    info = packageregistry.get_info("mknodes")
    assert info.license_name == "MIT"
    assert info.keywords
    assert info.extras is not None
    for package in info.required_package_names:
        packageregistry.get_info(package)

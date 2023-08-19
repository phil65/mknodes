from __future__ import annotations

from mknodes.info import packageinfo


def test_packageinfo():
    info = packageinfo.get_info("mknodes")
    assert info.license_name == "MIT"
    assert info.keywords
    assert info.extras is not None
    for package in info.required_package_names:
        packageinfo.get_info(package)

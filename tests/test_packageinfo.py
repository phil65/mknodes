from __future__ import annotations

from mknodes.utils import packageinfo


def test_packageinfo():
    info = packageinfo.get_info("mknodes")
    info.get_license()
    info.get_keywords()
    info.get_extras()
    for package in info.get_required_package_names():
        packageinfo.get_info(package)

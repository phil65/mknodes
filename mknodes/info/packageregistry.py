from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping

from mknodes.info import packageinfo
from mknodes.utils import log, packagehelpers


logger = log.get_logger(__name__)


def get_info(mod_name: str) -> packageinfo.PackageInfo:
    return registry.get_info(mod_name)


class PackageRegistry(MutableMapping, metaclass=ABCMeta):
    def __init__(self):
        self._packages: dict[str, packageinfo.PackageInfo] = {}

    def __getitem__(self, value):
        return self._packages.__getitem__(value)

    def __setitem__(self, index, value):
        self._packages[index] = value

    def __delitem__(self, index):
        del self._packages[index]

    def __repr__(self):
        return f"{type(self).__name__}({self.path!r})"

    def __iter__(self):
        return iter(self._packages.keys())

    def __len__(self):
        return len(self._packages)

    def get_info(self, mod_name: str) -> packageinfo.PackageInfo:
        mapping = packagehelpers.get_package_map()
        pkg_name = mapping[mod_name][0] if mod_name in mapping else mod_name
        pkg_name = pkg_name.lower()
        if pkg_name not in self._packages:
            self._packages[pkg_name] = packageinfo.PackageInfo(pkg_name)
        return self._packages[pkg_name]

    @property
    def inventory_urls(self):
        return {v.inventory_url for v in self.values() if v.inventory_url is not None}


registry = PackageRegistry()


if __name__ == "__main__":
    reg = PackageRegistry()
    info = reg.get_info("mknodes")
    print(info.get_entry_points("mkdocs.plugins"))
    print(info.cli)

from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping

from mknodes.info import packageinfo
from mknodes.utils import log, packagehelpers


logger = log.get_logger(__name__)


def get_info(mod_name: str) -> packageinfo.PackageInfo:
    """Return info for given module from registry.

    Arguments:
        mod_name: Name of the module
    """
    return registry.get_info(mod_name)


class PackageRegistry(MutableMapping, metaclass=ABCMeta):
    """Registry for PackageInfos.

    Used for caching all loaded Package information.
    """

    def __init__(self):
        self._packages: dict[str, packageinfo.PackageInfo] = {}

    def __getitem__(self, value):
        return self._packages.__getitem__(value)

    def __setitem__(self, index, value):
        self._packages[index] = value

    def __delitem__(self, index):
        del self._packages[index]

    def __repr__(self):
        return f"{type(self).__name__}()"

    def __iter__(self):
        return iter(self._packages.keys())

    def __len__(self):
        return len(self._packages)

    def get_info(self, mod_name: str) -> packageinfo.PackageInfo:
        """Get package information for given module.

        Arguments:
            mod_name: Name of the module
        """
        mapping = packagehelpers.get_package_map()
        pkg_name = mapping[mod_name][0] if mod_name in mapping else mod_name
        pkg_name = pkg_name.lower()
        if pkg_name not in self._packages:
            self._packages[pkg_name] = packageinfo.PackageInfo(pkg_name)
        return self._packages[pkg_name]

    @property
    def inventory_urls(self) -> set[str]:
        """Return a set of inventory urls for all loaded packages."""
        return {v.inventory_url for v in self.values() if v.inventory_url is not None}


registry = PackageRegistry()


if __name__ == "__main__":
    reg = PackageRegistry()
    info = reg.get_info("mknodes")

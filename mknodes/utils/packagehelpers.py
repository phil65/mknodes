from __future__ import annotations

import collections

from collections.abc import Mapping
import dataclasses
import functools
import importlib
from importlib import metadata
import types

from packaging.markers import Marker
from packaging.requirements import Requirement
import pip._internal as pip

from mknodes.utils import log


logger = log.get_logger(__name__)


def install(package: str, editable: bool = False):
    """Pip-Install distribution with given options.

    Arguments:
        package: Name of the package to install
        editable: Whether to install in editable mode
    """
    cmd = ["install", "-e", package] if editable else ["install", package]
    pip.main(cmd)


def install_or_import(module_name: str) -> types.ModuleType:
    """If required, try to install given package and import it.

    This method relies on module name == distribution_name

    Arguments:
        module_name: Name of the module to import / install
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        install(module_name)
        return importlib.import_module(module_name)


@functools.cache
def get_distribution(name: str) -> metadata.Distribution:
    """Cached version of metadata.distribution.

    Arguments:
        name: Name of the distribution to get an object for.
    """
    return metadata.distribution(name)


@functools.cache
def get_metadata(dist: metadata.Distribution):
    return dist.metadata


@functools.cache
def get_requires(dist: metadata.Distribution) -> list[str]:
    return dist.requires or []


@functools.cache
def get_package_map() -> Mapping[str, list[str]]:
    """Return a mapping of top-level packages to their distributions."""
    return metadata.packages_distributions()


@functools.cache
def distribution_to_package(dist: str):
    """Return the top-level package for given distribution.

    Arguments:
        dist: Name of the distribution to get the package for.
    """
    result = next((k for k, v in get_package_map().items() if dist in v), dist)
    return result.replace("-", "_").lower()


@functools.cache
def get_marker(marker):
    return Marker(marker)


@functools.cache
def _get_entry_points(dist: metadata.Distribution):
    return dist.entry_points


def get_extras(markers: list) -> list[str]:
    extras = []
    for marker in markers:
        match marker:
            case list():
                extras.extend(get_extras(marker))
            case tuple():
                if str(marker[0]) == "extra":
                    extras.append(str(marker[2]))
    return extras


@dataclasses.dataclass
class EntryPoint:
    """EntryPoint including imported module."""

    name: str
    dotted_path: str
    group: str

    def load(self) -> types.ModuleType | type:
        """Import and return the EntryPoint object."""
        if ":" in self.dotted_path:
            mod_name, kls_name = self.dotted_path.split(":")
        else:
            mod_name, kls_name = self.dotted_path, None
        mod = importlib.import_module(mod_name)
        return getattr(mod, kls_name) if kls_name else mod

    @property
    def module(self) -> str:
        """The module of the entry point."""
        return self.dotted_path.split(":")[0]

    @property
    def obj_path(self) -> str:
        """The dotted path of the object (without the module)."""
        return self.dotted_path.split(":")[1]


@functools.cache
def get_entry_points(
    dist: metadata.Distribution | str,
    group: str | None = None,
) -> collections.defaultdict[str, list[EntryPoint]]:
    """Returns a dictionary with entry point group as key, entry points as value.

    Arguments:
        dist: Distribution to get entry points for.
        group: Optional group filter.
    """
    if isinstance(dist, str):
        dist = get_distribution(dist)
    if not group:
        eps = _get_entry_points(dist)
    else:
        eps = [i for i in _get_entry_points(dist) if i.group == group]
    dct = collections.defaultdict(list)
    for ep in eps:
        ep = EntryPoint(name=ep.name, dotted_path=ep.value, group=ep.group)
        dct[ep.group].append(ep)
    return dct


class EntryPointMap(collections.defaultdict):
    def __init__(self):
        super().__init__(list)

    @property
    def all_eps(self):
        return [i for ls in self.values() for i in ls]


class Dependency:
    def __init__(self, name: str):
        self.req = Requirement(name)
        self.name = self.req.name
        self._marker = name

    @property
    def marker(self):
        return (
            get_marker(self._marker.split(";", maxsplit=1)[-1])
            if ";" in self._marker
            else None
        )

    @functools.cached_property
    def extras(self):
        return get_extras(self.marker._markers) if self.marker else []

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"


@functools.cache
def get_dependency(name) -> Dependency:
    return Dependency(name)


@functools.cache
def list_installed_packages() -> dict[str, str]:
    import pkg_resources

    return {i.project_name: i.key for i in pkg_resources.working_set}


if __name__ == "__main__":
    eps = list_installed_packages()
    print(eps)

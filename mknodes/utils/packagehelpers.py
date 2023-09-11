from __future__ import annotations

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
    cmd = ["install", "-e", package] if editable else ["install", package]
    pip.main(cmd)


def install_or_import(package: str) -> types.ModuleType:
    try:
        return importlib.import_module(package)
    except ImportError:
        install(package)
        return importlib.import_module(package)


@functools.cache
def get_distribution(name: str) -> metadata.Distribution:
    return metadata.distribution(name)


@functools.cache
def get_metadata(dist: metadata.Distribution):
    return dist.metadata


@functools.cache
def get_requires(dist: metadata.Distribution) -> list[str]:
    return dist.requires or []


@functools.cache
def get_package_map() -> Mapping[str, list[str]]:
    return metadata.packages_distributions()


@functools.cache
def distribution_to_package(dist: str):
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
    obj: types.ModuleType | type


@functools.cache
def get_entry_points(
    dist: metadata.Distribution | str,
    group: str | None = None,
) -> dict[str, EntryPoint]:
    if isinstance(dist, str):
        dist = get_distribution(dist)
    if not group:
        eps = _get_entry_points(dist)
    else:
        eps = [i for i in _get_entry_points(dist) if i.group == group]
    dct = {}
    for ep in eps:
        if ":" in ep.value:
            mod_name, kls_name = ep.value.split(":")
        else:
            mod_name, kls_name = ep.value, None
        mod = importlib.import_module(mod_name)
        dct[f"{ep.group}.{ep.name}"] = EntryPoint(
            name=ep.name,
            dotted_path=ep.value,
            group=ep.group,
            obj=getattr(mod, kls_name) if kls_name else mod,
        )
    return dct


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

from __future__ import annotations

import functools
import importlib
from importlib import metadata
from typing import TYPE_CHECKING

from packaging.markers import Marker
from packaging.requirements import Requirement
import pip._internal as pip

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Container
    import types


logger = log.get_logger(__name__)


def install(package: str, editable: bool = False):
    """Pip-Install distribution with given options.

    Args:
        package: Name of the package to install
        editable: Whether to install in editable mode
    """
    cmd = ["install", "-e", package] if editable else ["install", package]
    pip.main(cmd)


def install_or_import(module_name: str) -> types.ModuleType:
    """If required, try to install given package and import it.

    This method relies on module name == distribution_name

    Args:
        module_name: Name of the module to import / install
    """
    try:
        return importlib.import_module(module_name)
    except ImportError:
        install(module_name)
        return importlib.import_module(module_name)


@functools.cache
def get_requires(dist: metadata.Distribution) -> list[str]:
    return dist.requires or []


@functools.cache
def get_marker(marker) -> Marker:
    return Marker(marker)


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


def import_dotted_path(path: str) -> type | types.ModuleType:
    if ":" in path:
        mod_name, kls_name = path.split(":")
    else:
        mod_name, kls_name = path, None
    mod = importlib.import_module(mod_name)
    return getattr(mod, kls_name) if kls_name else mod


class Dependency:
    def __init__(self, name: str):
        self.req = Requirement(name)
        self.name = self.req.name
        self._marker = name

    @property
    def marker(self) -> Marker | None:
        return (
            get_marker(self._marker.split(";", maxsplit=1)[-1])
            if ";" in self._marker
            else None
        )

    @functools.cached_property
    def extras(self) -> list[str]:
        return get_extras(self.marker._markers) if self.marker else []

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"


@functools.cache
def get_dependency(name: str) -> Dependency:
    return Dependency(name)


@functools.cache
def list_installed_packages() -> dict[str, str]:
    import pkg_resources

    return {i.project_name: i.key for i in pkg_resources.working_set}


stdlib_pkgs = {"python", "wsgiref", "argparse"}


@functools.cache
def list_pip_packages(
    local_only: bool = True,
    user_only: bool = False,
    skip: Container[str] = stdlib_pkgs,
    include_editables: bool = True,
    editables_only: bool = False,
):
    """Returns a list of installed distributions.

    This is based on ``iter_all_distributions()`` with additional filtering
    options. Note that ``iter_installed_distributions()`` without arguments
    is *not* equal to ``iter_all_distributions()``, since some of the
    configurations exclude packages by default.

    Args:
        local_only:
            If True (default), only return installations local to the current
            virtualenv, if in a virtualenv.
        skip: iterable:
            An iterable of canonicalized project names to ignore.
            Defaults to ``stdlib_pkgs``.
        include_editables:
            If False, don't report editables.
        editables_only:
            If True, only report editables.
        user_only:
            If True, only report installations in the user site directory.

    Returns:
        list: A list of installed distribution packages.
    """
    # import warnings

    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore")

    from pip._internal.metadata import pkg_resources

    return list(
        pkg_resources.Environment.from_paths(None).iter_installed_distributions(
            local_only=local_only,
            skip=skip,
            user_only=user_only,
            include_editables=include_editables,
            editables_only=editables_only,
        )
    )


if __name__ == "__main__":
    eps = list_installed_packages()
    print(eps)

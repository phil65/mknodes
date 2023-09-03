from __future__ import annotations

from collections.abc import Mapping
import contextlib
import functools
import importlib

from importlib import metadata
import logging
from typing import Literal

from packaging.markers import Marker
from packaging.requirements import Requirement

from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


ClassifierStr = Literal[
    "Development Status",
    "Environment",
    "Framework",
    "Intended Audience",
    "License",
    "Natural Language",
    "Operating System",
    "Programming Language",
    "Topic",
    "Typing",
]

CLASSIFIERS: list[ClassifierStr] = [
    "Development Status",
    "Environment",
    "Framework",
    "Intended Audience",
    "License",
    "Natural Language",
    "Operating System",
    "Programming Language",
    "Topic",
    "Typing",
]


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


class Dependency:
    def __init__(self, name: str):
        self.req = Requirement(name)
        self.name = self.req.name
        self.marker = Marker(name.split(";", maxsplit=1)[-1]) if ";" in name else None
        self.extras = get_extras(self.marker._markers) if self.marker else []

    def __repr__(self):
        return f"{type(self).__name__}(name={self.name!r})"


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
def get_dependency(name) -> Dependency:
    return Dependency(name)


registry: dict[str, PackageInfo] = {}


@functools.cache
def get_package_map() -> Mapping[str, list[str]]:
    return metadata.packages_distributions()


def get_info(pkg_name: str) -> PackageInfo:
    mapping = get_package_map()
    if pkg_name in mapping:
        pkg_name = mapping[pkg_name][0]
    if pkg_name in registry:
        return registry[pkg_name]
    registry[pkg_name] = PackageInfo(pkg_name)
    return registry[pkg_name]


class PackageInfo:
    def __init__(self, pkg_name: str):
        self.package_name = pkg_name
        logger.info("Loading package info for %s", pkg_name)
        self.distribution = get_distribution(pkg_name)
        self.metadata = get_metadata(self.distribution)
        self.urls = {
            v.split(",")[0].strip(): v.split(",")[1].strip()
            for k, v in self.metadata.items()
            if k == "Project-URL"
        }
        if "Home-page" in self.metadata:
            self.urls["Home-page"] = self.metadata["Home-page"].strip()
        self.classifiers = [v for h, v in self.metadata.items() if h == "Classifier"]
        self.version = self.metadata["Version"]
        self.metadata_version = self.metadata["Metadata-Version"]
        self.name = self.metadata["Name"]

    def __repr__(self):
        return reprhelpers.get_repr(self, pkg_name=self.package_name)

    def __hash__(self):
        return hash(self.package_name)

    @functools.cached_property
    def required_deps(self) -> list[Dependency]:
        requires = get_requires(self.distribution)
        return [get_dependency(i) for i in requires] if requires else []

    @property
    def license_name(self) -> str | None:
        """Get name of the license."""
        if license_name := self.metadata.get("License-Expression", "").strip():
            return license_name
        return next(
            (
                value.rsplit("::", 1)[1].strip()
                for header, value in self.metadata.items()
                if header == "Classifier" and value.startswith("License ::")
            ),
            None,
        )

    @property
    def repository_url(self) -> str | None:
        """Return repository URL from metadata."""
        return next(
            (
                self.urls[tag]
                for tag in ["Source", "Repository", "Source Code"]
                if tag in self.urls
            ),
            None,
        )

    @property
    def homepage(self) -> str | None:
        if "Home-page" in self.urls:
            return self.urls["Home-page"]
        if "Homepage" in self.urls:
            return self.urls["Homepage"]
        if "Documentation" in self.urls:
            return self.urls["Documentation"]
        return self.repository_url

    @property
    def keywords(self) -> list[str]:
        """Return a list of keywords from metadata."""
        return self.metadata.get("Keywords", "").split(",")

    @property
    def classifier_map(self) -> dict[str, list[str]]:
        """Return a dict containing the classifier categories and values from metadata.

        {category_1: [classifier_1, ...],
         category_2, [classifier_x, ...],
         ...
         }
        """
        classifiers: dict[str, list[str]] = {}
        for k, v in self.metadata.items():
            if k == "Classifier":
                category, value = v.split(" :: ", 1)
                if category in classifiers:
                    classifiers[category].append(value)
                else:
                    classifiers[category] = [value]
        return classifiers

    @property
    def required_package_names(self) -> list[str]:
        """Get a list of names from required packages."""
        return [i.name for i in self.required_deps]

    @property
    def author_email(self) -> str:
        mail = self.metadata["Author-email"].split(" ")[-1]
        return mail.replace("<", "").replace(">", "")

    @property
    def author_name(self) -> str:
        return self.metadata["Author-email"].rsplit(" ", 1)[0]

    @property
    def authors(self) -> dict[str, str]:
        """Return a dict containing the authors.

        {author 1: email of author 1,
         author_2, email of author 2,
         ...
         }
        """
        authors: dict[str, str] = {}
        for k, v in self.metadata.items():
            if k == "Author-email":
                mail = v.split(" ")[-1]
                mail = mail.replace("<", "").replace(">", "")
                name = v.rsplit(" ", 1)[0]
                authors[name] = mail
        return authors

    @property
    def extras(self) -> dict[str, list[str]]:
        """Return a dict containing extras and the packages {extra: [package_1, ...]}."""
        extras: dict[str, list[str]] = {}
        for dep in self.required_deps:
            for extra in dep.extras:
                if extra in extras:
                    extras[extra].append(dep.name)
                else:
                    extras[extra] = [dep.name]
        return extras

    @property
    def required_python_version(self) -> str | None:
        return self.metadata.json.get("requires_python")

    def get_required_packages(self) -> dict[PackageInfo, Dependency]:
        modules = (
            {Requirement(i).name for i in get_requires(self.distribution)}
            if get_requires(self.distribution)
            else set()
        )
        packages = {}
        for mod in modules:
            with contextlib.suppress(Exception):
                packages[get_info(mod)] = self.get_dep_info(mod)
        return packages

    def get_dep_info(self, name: str) -> Dependency:
        for i in self.required_deps:
            if i.name == name:
                return i
        raise ValueError(name)

    def get_entry_points(self, group: str | None = None) -> dict[str, type]:
        if not group:
            eps = self.distribution.entry_points
        else:
            eps = [i for i in self.distribution.entry_points if i.group == group]
        dct = {}
        for ep in eps:
            name, dotted_path = ep.name, ep.value
            mod_name, kls_name = dotted_path.split(":")
            mod = importlib.import_module(mod_name)
            dct[name] = getattr(mod, kls_name)
        return dct


if __name__ == "__main__":
    info = get_info("mknodes")
    print(info.get_entry_points())

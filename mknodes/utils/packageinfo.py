from __future__ import annotations

import contextlib
import functools

from importlib import metadata
import pathlib
import re
from typing import Literal

from packaging.markers import Marker
from packaging.requirements import Requirement

from mknodes.utils import helpers


GITHUB_REGEX = re.compile(
    r"(?:http?:\/\/|https?:\/\/)?"
    r"(?:www\.)?"
    r"github\.com\/"
    r"(?:\/*)"
    r"([\w\-\.]*)\/"
    r"([\w\-]*)"
    r"(?:\/|$)?"  # noqa: COM812
)

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
def get_distribution(name):
    return metadata.distribution(name)


@functools.cache
def get_metadata(dist):
    return dist.metadata


@functools.cache
def get_requires(dist):
    return dist.requires


@functools.cache
def get_dependency(name):
    return Dependency(name)


registry: dict[str, PackageInfo] = {}


def get_info(pkg_name):
    if pkg_name in registry:
        return registry[pkg_name]
    registry[pkg_name] = PackageInfo(pkg_name)
    return registry[pkg_name]


class PackageInfo:
    def __init__(self, pkg_name: str):
        self.package_name = pkg_name
        self.distribution = get_distribution(pkg_name)
        self.metadata = get_metadata(self.distribution)
        self.urls = {
            v.split(",")[0].strip(): v.split(",")[1].strip()
            for k, v in self.metadata.items()
            if k == "Project-URL"
        }
        if "Home-page" in self.metadata:
            self.urls["Home-page"] = self.metadata["Home-page"].strip()
        requires = get_requires(self.distribution)
        self.required_deps = [get_dependency(i) for i in requires] if requires else []
        self.classifiers = [v for h, v in self.metadata.items() if h == "Classifier"]
        self.version = self.metadata["Version"]
        self.metadata_version = self.metadata["Metadata-Version"]
        self.name = self.metadata["Name"]

    def __repr__(self):
        return helpers.get_repr(self, pkg_name=self.package_name)

    def __hash__(self):
        return hash(self.package_name)

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
        return self.repository_url

    @property
    def repository_username(self) -> str | None:
        """Try to extract repository username from metadata."""
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(1)
        return None

    @property
    def repository_name(self) -> str | None:
        """Try to extract repository name from metadata."""
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(2)
        return None

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

    def get_license_file_path(self) -> pathlib.Path | None:
        """Return license file path (relative to project root) from metadata."""
        for path in ["LICENSE", "LICENSE.md", "LICENSE.txt"]:
            if (file := pathlib.Path(path)).exists():
                return file
        if file := self.metadata.get("License-File"):
            return pathlib.Path(file)
        return None

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


if __name__ == "__main__":
    info = get_info("anybadge")
    print(info.repository_url)

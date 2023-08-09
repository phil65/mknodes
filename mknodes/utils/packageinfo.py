from __future__ import annotations

import contextlib
import functools

from importlib import metadata
import pathlib
import re

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

CLASSIFIERS = [
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


class PackageInfo:
    def __init__(self, pkg_name: str):
        self.package_name = pkg_name
        self.distribution = get_distribution(pkg_name)
        self.metadata = get_metadata(self.distribution)
        self.urls = {
            v.split(",")[0]: v.split(",")[1]
            for k, v in self.metadata.items()
            if k == "Project-URL"
        }
        requires = get_requires(self.distribution)
        self.requirements = [get_dependency(i) for i in requires] if requires else []
        self.classifiers = [v for h, v in self.metadata.items() if h == "Classifier"]
        self.version = self.metadata["Version"]
        self.metadata_version = self.metadata["Metadata-Version"]
        self.name = self.metadata["Name"]

    def __repr__(self):
        return helpers.get_repr(self, pkg_name=self.package_name)

    def get_license(self) -> str:
        if license_name := self.metadata.get("License-Expression", "").strip():
            return license_name
        return next(
            (
                value.rsplit("::", 1)[1].strip()
                for header, value in self.metadata.items()
                if header == "Classifier" and value.startswith("License ::")
            ),
            "Unknown",
        )

    def get_license_file_path(self) -> pathlib.Path | None:
        file = self.metadata.get("License-File")
        return pathlib.Path(file) if file else None

    def get_repository_url(self) -> str | None:
        if "Source" in self.urls:
            return self.urls["Source"]
        return self.urls["Repository"] if "Repository" in self.urls else None

    def get_repository_username(self) -> str | None:
        if match := GITHUB_REGEX.match(self.get_repository_url() or ""):
            return match.group(1)
        return None

    def get_repository_name(self) -> str | None:
        if match := GITHUB_REGEX.match(self.get_repository_url() or ""):
            return match.group(2)
        return None

    def get_keywords(self) -> list[str]:
        return self.metadata.get("Keywords", "").split(",")

    def get_required_package_names(self) -> list[str]:
        return [i.name for i in self.requirements]

    def get_required_packages(self) -> dict[PackageInfo, Dependency]:
        modules = (
            {Requirement(i).name for i in get_requires(self.distribution)}
            if get_requires(self.distribution)
            else set()
        )
        packages = {}
        for mod in modules:
            with contextlib.suppress(Exception):
                packages[PackageInfo(mod)] = self.get_dep_info(mod)
        return packages

    def get_dep_info(self, name):
        for i in self.requirements:
            if i.name == name:
                return i
        raise ValueError(name)

    def get_extras(self) -> set[str]:
        return {extra for dep in self.requirements for extra in dep.extras}

    def get_author_email(self) -> str:
        mail = self.metadata["Author-Email"].split(" ")[-1]
        return mail.replace("<", "").replace(">", "")


if __name__ == "__main__":
    info = PackageInfo("mknodes")
    print(info.metadata)

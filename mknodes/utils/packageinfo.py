from __future__ import annotations

from importlib import metadata
import pathlib

from packaging.markers import Marker
from packaging.requirements import Requirement
import toml

from mknodes.utils import helpers


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


class PackageInfo:
    def __init__(self, pkg_name: str, pyproject_path: str | None = None):
        self.package_name = pkg_name
        self.distribution = metadata.distribution(pkg_name)
        self.metadata = self.distribution.metadata
        self.urls = {
            v.split(",")[0]: v.split(",")[1]
            for k, v in self.metadata.items()
            if k == "Project-URL"
        }
        requires = self.distribution.requires
        self.requirements = [Dependency(i) for i in requires] if requires else []
        self.classifiers = [v for h, v in self.metadata.items() if h == "Classifier"]
        self.version = self.metadata["Version"]
        self.metadata_version = self.metadata["Metadata-Version"]
        self.name = self.metadata["Name"]
        if not pyproject_path and (path := pathlib.Path() / "pyproject.toml").exists():
            self.pyproject = toml.load(path)
        elif pyproject_path:
            if pyproject_path.startswith(("http:", "https:")):
                content = helpers.download(pyproject_path)
                self.pyproject = toml.loads(content)
            else:
                self.pyproject = toml.load(pyproject_path)

    def configured_build_systems(self) -> list[str]:
        build_systems = ["poetry", "hatch", "pdm", "flit"]
        return [b for b in build_systems if b in self.pyproject["tool"]]

    def build_system(self) -> str:
        back_end = self.pyproject["build-system"]["build-backend"]
        match back_end:
            case "hatchling.build":
                return "hatch"
            case "poetry.core.masonry.api":
                return "poetry"
            case "setuptools.build_meta":
                return "setuptools"
            case "flit_core.buildapi":
                return "flit"
            case "pdm.backend":
                return "pdm"
            case _:
                msg = "No known build backend"
                raise RuntimeError(msg)

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

    def get_repository_url(self) -> str | None:
        if "Source" in self.urls:
            return self.urls["Source"]
        return self.urls["Repository"] if "Repository" in self.urls else None

    def get_keywords(self) -> list[str]:
        return self.metadata.get("Keywords", "").split(",")

    def get_required_package_names(self) -> list[str]:
        return [i.name for i in self.requirements]

    def get_extras(self) -> set[str]:
        return {extra for dep in self.requirements for extra in dep.extras}

    def get_license_file_path(self) -> pathlib.Path | None:
        file = self.metadata.get("License-File")
        return pathlib.Path(file) if file else None


if __name__ == "__main__":
    info = PackageInfo(
        "mkdocs",
        pyproject_path=(
            "https://raw.githubusercontent.com/mkdocs/mkdocs/master/pyproject.toml"
        ),
    )
    print(info.configured_build_systems())
    # print(info.get_github_url())

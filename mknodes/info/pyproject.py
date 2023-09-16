from __future__ import annotations

import collections
import functools
import os
import pathlib

from typing import Any

from mknodes.data import buildsystems, commitconventions, installmethods
from mknodes.info import tomlfile
from mknodes.utils import pathhelpers, superdict


class PyProject(tomlfile.TomlFile):
    """Class representing a PyProject config file."""

    def __init__(self, path: str | os.PathLike | None = None):
        """Constructor.

        Arguments:
            path: Path to the pyproject file.
                  If None, parent directories are checked, too.
                  If path points to folder, check that folder for a pyproject.toml
                  Otherwise, take file from explicit path.
        """
        if path is None:
            path = pathhelpers.find_file_in_folder_or_parent("pyproject.toml")
        if path is None:
            msg = "Could not find pyproject.toml"
            raise FileNotFoundError(msg)
        path = pathlib.Path(path)
        if path.is_dir():
            path = path / "pyproject.toml"
        super().__init__(path)

    @property
    def mknodes_section(self):
        return self.get_section("tool", "mknodes") or {}

    @property
    def name(self) -> str | None:
        """Project name."""
        return self.project.get("name")

    @property
    def tool(self) -> superdict.SuperDict[Any]:
        """Tool section."""
        dct: collections.defaultdict[str, dict] = collections.defaultdict(dict)
        dct.update(self._data.get("tool", {}))
        return superdict.SuperDict(dct)

    @property
    def project(self) -> dict[str, Any]:
        """Project section."""
        return self._data.get("project", {})

    @functools.cached_property
    def configured_build_systems(self) -> list[buildsystems.BuildSystemStr]:
        """Return build systems which have a config in tools section."""
        return [p for p in buildsystems.BUILD_SYSTEMS if p in self.tool]

    @functools.cached_property
    def build_system(self) -> buildsystems.BuildSystem:
        """Return the build system set as build backend."""
        back_end = self._data["build-system"]["build-backend"]
        for p in buildsystems.BUILD_SYSTEMS.values():
            if p.build_backend == back_end:
                return p
        msg = "No known build backend"
        raise RuntimeError(msg)

    @property
    def allowed_commit_types(self) -> list[commitconventions.CommitTypeStr]:
        """Return the allowed commit types."""
        return self.mknodes_section.get("allowed-commit-types", [])

    @property
    def extras_descriptions(self) -> dict[str, str]:
        """Return a dictionary with descriptions for dependency extras."""
        return self.mknodes_section.get("extras-descriptions", {})

    @property
    def package_repos(self) -> list[installmethods.InstallMethodStr]:
        """Return a list of package repositories the package is available on."""
        return self.mknodes_section.get("package-repositories", ["pip"])

    @property
    def docstring_style(self) -> str | None:
        """Return the style used for docstring."""
        return self.mknodes_section.get("docstring-style")

    @property
    def line_length(self) -> int | None:
        # sourcery skip: assign-if-exp, reintroduce-else
        """Return the line length (taken from black / ruff / isort config)."""
        if length := self.tool["ruff"].get("line-length"):
            return int(length)
        if length := self.tool["isort"].get("line_length"):
            return int(length)
        if length := self.tool["black"].get("line-length"):
            return int(length)
        return None

    @property
    def min_tool_python_version(self) -> tuple[int, int] | None:
        """Return python target version of the tools.

        Taken from black / ruff / mypy config.
        """
        if version := self.tool["mypy"].get("python_version"):
            return (3, int(version[-2:]))
        if version := self.tool["black"].get("target-version"):
            return (3, int(version[-2:]))
        if version := self.tool["ruff"].get("target-version"):
            return (3, int(version[-2:]))
        return None

    # @functools.cached_property
    # def context(self):
    #     return contexts.PyProjectContext(
    #         extras_descriptions=self.extras_descriptions,
    #         configured_build_systems=self.configured_build_systems,
    #         build_system=self.build_system,
    #         package_repos=self.package_repos,
    #         commit_types=self.allowed_commit_types,
    #         docstring_style=self.docstring_style,
    #         line_length=self.line_length,
    #         tool_section=self.tool,
    #     )


if __name__ == "__main__":
    info = PyProject()
    print(info.min_tool_python_version)

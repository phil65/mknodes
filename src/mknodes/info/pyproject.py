from __future__ import annotations

import collections
import functools
from typing import TYPE_CHECKING, Any

from upathtools import to_upath

from mknodes.data import buildsystems
from mknodes.info import configfile
from mknodes.utils import pathhelpers, superdict


if TYPE_CHECKING:
    import os

    import upath

    from mknodes.data import commitconventions, installmethods


class PyProject(configfile.TomlFile):
    """Class representing a PyProject config file."""

    def __init__(self, path: str | os.PathLike[str] | upath.UPath | None = None) -> None:
        """Constructor.

        Args:
            path: Path to the pyproject file.
                  If None, parent directories are checked, too.
                  If path points to folder, check that folder for a pyproject.toml
                  Otherwise, take file from explicit path.
        """
        if path is None:
            path = pathhelpers.find_cfg_for_folder("pyproject.toml")
        if path is None:
            msg = "Could not find pyproject.toml"
            raise FileNotFoundError(msg)
        p = to_upath(path)
        if p.is_dir():
            p /= "pyproject.toml"
        super().__init__(p)

    @property
    def mknodes_section(self) -> dict[str, Any]:
        """Return our very own config section."""
        return self.get_section("tool", "mknodes") or {}

    @property
    def name(self) -> str | None:
        """Project name."""
        return self.project.get("name")

    @property
    def tool(self) -> superdict.SuperDict[Any]:
        """Tool section."""
        dct: collections.defaultdict[str, dict[str, Any]] = collections.defaultdict(dict)
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
        return buildsystems.BuildSystem(
            build_backend=back_end,
            identifier=back_end,
            url="",
            env_setup_cmd="",
        )

    @property
    def allowed_commit_types(self) -> list[commitconventions.CommitTypeStr]:
        """Return the allowed commit types."""
        return self.mknodes_section.get("allowed-commit-types", [])

    @property
    def package_repos(self) -> list[installmethods.InstallMethodStr]:
        """Return a list of package repositories the package is available on."""
        return self.mknodes_section.get("package-repositories", [])

    @property
    def docstring_style(self) -> str | None:
        """Return the style used for docstring."""
        if convention := self.tool.get("pydocstyle", {}).get("convention"):
            return convention
        return self.mknodes_section.get("docstring-style")

    @property
    def cli_obj_path(self) -> str | None:
        """Return path to the object describing the CLI, used for documenting the CLI.

        Path can lead to:

        * click.Group instance
        * typer.Typer instance
        * ArgumentParser instance
        * cappa dataclass

        """
        return self.mknodes_section.get("cli-obj-path")

    # @functools.cached_property
    # def context(self):
    #     return contexts.PyProjectContext(
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

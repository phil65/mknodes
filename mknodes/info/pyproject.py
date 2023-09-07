from __future__ import annotations

import os
import pathlib

from typing import Any

from mknodes.data import buildsystems, commitconventions, installmethods
from mknodes.info import tomlfile
from mknodes.utils import helpers


class PyProject(tomlfile.TomlFile):
    def __init__(self, path: str | os.PathLike | None = None):
        if path is None:
            path = helpers.find_file_in_folder_or_parent("pyproject.toml")
        if path is None:
            msg = "Could not find pyproject.toml"
            raise FileNotFoundError(msg)
        path = pathlib.Path(path)
        if path.is_dir():
            path = path / "pyproject.toml"
        super().__init__(path)
        self.mknodes_section = self.get_section("tool", "mknodes")

    def __repr__(self):
        return f"PyProject({self.name!r})"

    @property
    def name(self) -> str:
        return self.project["name"]

    @property
    def tool(self) -> dict[str, Any]:
        return self._data.get("tool", {})

    @property
    def project(self) -> dict[str, Any]:
        return self._data.get("project", {})

    @property
    def configured_build_systems(self) -> list[buildsystems.BuildSystemStr]:
        return [p for p in buildsystems.BUILD_SYSTEMS if p in self.tool]

    @property
    def build_system(self) -> buildsystems.BuildSystem:
        back_end = self._data["build-system"]["build-backend"]
        for p in buildsystems.BUILD_SYSTEMS.values():
            if p.build_backend == back_end:
                return p
        msg = "No known build backend"
        raise RuntimeError(msg)

    @property
    def allowed_commit_types(self) -> list[commitconventions.CommitTypeStr]:
        return self.mknodes_section.get("allowed-commit-types", [])

    @property
    def extras_descriptions(self) -> dict[str, str]:
        return self.mknodes_section.get("extras-descriptions", {})

    @property
    def package_repos(self) -> list[installmethods.InstallMethodStr]:
        return self.mknodes_section.get("package-repositories", ["pip"])


if __name__ == "__main__":
    info = PyProject()
    print(info)

from __future__ import annotations

import os
import tomllib

from mknodes.data import buildsystems
from mknodes.utils import helpers


class PyProject:
    def __init__(self, pyproject_path: str | os.PathLike | None = None):
        if helpers.is_url(str(pyproject_path)):
            content = helpers.download(str(pyproject_path))
            self._data = tomllib.loads(content)
        else:
            folder = pyproject_path or "."
            path = helpers.find_file_in_folder_or_parent("pyproject.toml", folder)
            if path is None:
                msg = "Could not find pyproject.toml"
                raise FileNotFoundError(msg)
            self._data = tomllib.loads(path.read_text())
        self.mknodes_section = self._data["tool"].get("mknodes", {})

    def __repr__(self):
        return f"PyProject({self._data['project']})"

    @property
    def configured_build_systems(self) -> list[buildsystems.BuildSystemStr]:
        return [p for p in buildsystems.BUILD_SYSTEMS if p in self._data["tool"]]

    @property
    def build_system(self) -> buildsystems.BuildSystem:
        back_end = self._data["build-system"]["build-backend"]
        for p in buildsystems.BUILD_SYSTEMS.values():
            if p.build_backend == back_end:
                return p
        msg = "No known build backend"
        raise RuntimeError(msg)

    @property
    def name(self) -> str:
        return self._data["project"]["name"]

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._data["tool"]

    @property
    def allowed_commit_types(self) -> list[str]:
        return self.mknodes_section.get("allowed-commit-types", [])

    @property
    def extras_descriptions(self) -> dict[str, str]:
        return self.mknodes_section.get("extras-descriptions", {})

    @property
    def package_repos(self) -> list[str]:
        return self.mknodes_section.get("package-repositories", ["pip"])


if __name__ == "__main__":
    info = PyProject()
    print(info)

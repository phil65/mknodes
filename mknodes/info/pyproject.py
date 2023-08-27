from __future__ import annotations

import os
import pathlib
import tomllib

from mknodes.data import buildsystems
from mknodes.utils import helpers


class PyProject:
    def __init__(self, pyproject_path: str | os.PathLike | None = None):
        path = pathlib.Path().absolute()
        if not pyproject_path:
            while not (path / "pyproject.toml").exists() and path.parent is not None:
                path = path.parent
            if path.parent is None:
                msg = "Could not find pyproject.toml"
                raise FileNotFoundError(msg)
            file = path / "pyproject.toml"
            self._data = tomllib.loads(file.read_text())

        elif helpers.is_url(str(pyproject_path)):
            content = helpers.download(str(pyproject_path))
            self._data = tomllib.loads(content)
        else:
            local_path = pathlib.Path(pyproject_path)
            text = local_path.read_text()
            self._data = tomllib.loads(text)
        self.mknodes_section = self._data["tool"].get("mknodes", {})

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
    print(info.extras_descriptions)

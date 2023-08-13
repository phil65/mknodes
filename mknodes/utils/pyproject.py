from __future__ import annotations

import pathlib

import toml

from mknodes.data import buildsystems
from mknodes.utils import helpers


class PyProject:
    def __init__(self, pyproject_path: str | None = None):
        path = pathlib.Path().absolute()
        if not pyproject_path:
            while not (path / "pyproject.toml").exists() and path.parent is not None:
                path = path.parent
            if path.parent is None:
                msg = "Could not find pyproject.toml"
                raise FileNotFoundError(msg)
            self._data = toml.load(path / "pyproject.toml")

        elif pyproject_path.startswith(("http:", "https:")):
            content = helpers.download(pyproject_path)
            self._data = toml.loads(content)
        else:
            self._data = toml.load(pyproject_path)
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

    def has_tool(self, tool_name: str) -> bool:
        return tool_name in self._data["tool"]

    @property
    def allowed_commit_types(self) -> list[str]:
        return self.mknodes_section.get("allowed-commit-types", [])

    @property
    def extras_descriptions(self) -> dict[str, str]:
        return self.mknodes_section.get("extras-descriptions", {})


if __name__ == "__main__":
    info = PyProject()
    print(info.get_allowed_commit_types())

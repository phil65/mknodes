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
            self.pyproject = toml.load(path / "pyproject.toml")

        elif pyproject_path.startswith(("http:", "https:")):
            content = helpers.download(pyproject_path)
            self.pyproject = toml.loads(content)
        else:
            self.pyproject = toml.load(pyproject_path)

    def configured_build_systems(self) -> list[str]:
        build_systems = ["poetry", "hatch", "pdm", "flit"]
        return [b for b in build_systems if b in self.pyproject["tool"]]

    def build_system(self) -> str:
        back_end = self.pyproject["build-system"]["build-backend"]
        for p in buildsystems.BUILD_SYSTEMS.values():
            if p.build_backend == back_end:
                return p.identifier
        msg = "No known build backend"
        raise RuntimeError(msg)

    def has_mypy(self) -> bool:
        return "mypy" in self.pyproject["tool"]

    def has_ruff(self) -> bool:
        return "ruff" in self.pyproject["tool"]

    def has_black(self) -> bool:
        return "black" in self.pyproject["tool"]

    def has_pytest(self) -> bool:
        return "pytest" in self.pyproject["tool"]

    def has_coverage(self) -> bool:
        return "coverage" in self.pyproject["tool"]


if __name__ == "__main__":
    info = PyProject()
    print(info.configured_build_systems())

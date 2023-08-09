from __future__ import annotations

import pathlib

import toml

from mknodes.utils import helpers


class PyProject:
    def __init__(self, pyproject_path: str | None = None):
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

    def has_mypy(self) -> bool:
        return "mypy" in self.pyproject["tool"]

    def has_ruff(self) -> bool:
        return "ruff" in self.pyproject["tool"]

    def has_black(self) -> bool:
        return "ruff" in self.pyproject["tool"]

    def has_pytest(self) -> bool:
        return "ruff" in self.pyproject["tool"]

    def has_coverage(self) -> bool:
        return "coverage" in self.pyproject["tool"]


if __name__ == "__main__":
    info = PyProject(
        pyproject_path=(
            "https://raw.githubusercontent.com/mkdocs/mkdocs/master/pyproject.toml"
        ),
    )
    print(info.configured_build_systems())

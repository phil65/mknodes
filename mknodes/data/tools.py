from __future__ import annotations

from typing import Literal

from mknodes.info import folderinfo
from mknodes.utils import helpers


ToolStr = Literal["pre-commit", "ruff", "mypy"]

PRE_COMMIT_CODE = """
# Setup pre-commit hooks for required formatting
pre-commit install
"""

PRE_COMMIT_TEXT = """This project uses `pre-commit` to ensure code quality.
A .pre-commit-config.yaml configuration file tailored for this project is provided
in the root folder."""


MYPY_CODE = """
mypy --help
"""

MYPY_TEXT = """MyPy is used for type checking. You can find the configuration in the
pyproject.toml file."""

RUFF_CODE = """
ruff --help
"""

RUFF_TEXT = """Ruff is used as a linter. You can find the configuration in the
pyproject.toml file."""


class Tool:
    identifier: ToolStr
    title: str
    url: str
    description: str
    setup_cmd: str

    def is_used(self, folder: folderinfo.FolderInfo | None = None) -> bool:
        """Return whether tool is used for given directory.

        Arguments:
            folder: Folder to check. Defaults to current working directory.
        """
        raise NotImplementedError

    def get_config(self, folder) -> str | None:
        """Return config for given tool.

        Arguments:
            folder: Folder to get config from. Defaults to current working directory.
        """
        return None


class PreCommit(Tool):
    identifier = "pre-commit"
    title = "Pre-Commit"
    url = "https://pre-commit.com"
    description = PRE_COMMIT_TEXT
    setup_cmd = PRE_COMMIT_CODE

    def is_used(self, folder: folderinfo.FolderInfo | None = None):
        directory = folder.path if folder else "."
        filename = ".pre-commit-config.yaml"
        return bool(helpers.find_file_in_folder_or_parent(filename, str(directory)))


class Ruff(Tool):
    identifier = "ruff"
    title = "Ruff"
    url = "https://beta.ruff.rs/"
    description = RUFF_TEXT
    setup_cmd = RUFF_CODE

    def is_used(self, folder: folderinfo.FolderInfo | None = None):
        return folder.pyproject.has_tool("ruff") if folder else False

    def get_config(self, folder):
        folder.pyproject.get_tool("ruff")


class MyPy(Tool):
    identifier = "mypy"
    title = "MyPy"
    url = "https://mypy-lang.org"
    description = MYPY_TEXT
    setup_cmd = MYPY_CODE

    def is_used(self, folder: folderinfo.FolderInfo | None = None):
        return folder.pyproject.has_tool("mypy") if folder else False

    def get_config(self, folder):
        folder.pyproject.get_tool("mypy")


TOOLS: dict[ToolStr, Tool] = {p.identifier: p for p in [PreCommit(), Ruff(), MyPy()]}

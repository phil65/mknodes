from __future__ import annotations

from typing import Literal

from mknodes.utils import helpers


ToolStr = Literal["pre-commit"]

PRE_COMMIT_CODE = """
# Setup pre-commit hooks for required formatting
pre-commit install
"""

PRE_COMMIT_TEXT = """This project uses `pre-commit` to ensure code quality.
A .pre-commit-config.yaml configuration file tailored for this project is provided
in the root folder."""


class Tool:
    identifier: ToolStr
    title: str
    url: str
    description: str
    setup_cmd: str

    def is_used(self, folder=None) -> bool:
        """Return whether tool is used for given directory.

        Arguments:
            folder: Folder to check. Defaults to current working directory.
        """
        raise NotImplementedError


class PreCommit(Tool):
    identifier = "pre-commit"
    title = "Pre-Commit"
    url = "https://pre-commit.com"
    description = PRE_COMMIT_TEXT
    setup_cmd = PRE_COMMIT_CODE

    def is_used(self, folder=None):
        folder = folder or "."
        filename = ".pre-commit-config.yaml"
        return bool(helpers.find_file_in_folder_or_parent(filename, folder))


TOOLS: dict[ToolStr, Tool] = {p.identifier: p for p in [PreCommit()]}

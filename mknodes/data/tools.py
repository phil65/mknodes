from __future__ import annotations

from typing import Literal

from mknodes.info import folderinfo
from mknodes.utils import helpers, yamlhelpers


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

BLACK_CODE = """
black .
"""

BLACK_TEXT = """Black is used as a code formatter. You can find the configuration in the
pyproject.toml file."""

COVERAGE_CODE = """
coverage run some_module.py
"""

COVERAGE_TEXT = """Coverage is used to monitor test coverage."""

MKDOCS_CODE = """
# To build the docs
mkdocs build

# To serve the docs locally at http://127.0.0.1:8000/
mkdocs serve

# For additional mkdocs help and options:
mkdocs --help
"""

MKDOCS_TEXT = """MkDocs is used to create the documentation."""


MATERIAL_TEXT = """Material for MkDocs is used as the Website theme."""


class Tool:
    identifier: ToolStr
    title: str
    url: str
    description: str
    setup_cmd: str | None
    config_syntax: str

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        """Return whether tool is used for given directory.

        Arguments:
            folder: Folder to check. Defaults to current working directory.
        """
        raise NotImplementedError

    def get_config(self, folder: folderinfo.FolderInfo) -> str | None:
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
    config_syntax = "yaml"

    def is_used(self, folder: folderinfo.FolderInfo):
        directory = folder.path if folder else "."
        filename = ".pre-commit-config.yaml"
        return bool(helpers.find_file_in_folder_or_parent(filename, str(directory)))

    def get_config(self, folder):
        directory = folder.path if folder else "."
        filename = ".pre-commit-config.yaml"
        path = helpers.find_file_in_folder_or_parent(filename, str(directory))
        return path.read_text() if path else None


class Ruff(Tool):
    identifier = "ruff"
    title = "Ruff"
    url = "https://beta.ruff.rs/"
    description = RUFF_TEXT
    setup_cmd = RUFF_CODE
    config_syntax = "toml"

    def is_used(self, folder: folderinfo.FolderInfo):
        return "ruff" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "ruff")


class Black(Tool):
    identifier = "black"
    title = "Black"
    url = "https://github.com/psf/black"
    description = BLACK_TEXT
    setup_cmd = BLACK_CODE
    config_syntax = "toml"

    def is_used(self, folder: folderinfo.FolderInfo):
        return "black" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "black")


class MyPy(Tool):
    identifier = "mypy"
    title = "MyPy"
    url = "https://mypy-lang.org"
    description = MYPY_TEXT
    setup_cmd = MYPY_CODE
    config_syntax = "toml"

    def is_used(self, folder: folderinfo.FolderInfo):
        return "mypy" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "mypy")


class Coverage(Tool):
    identifier = "coverage"
    title = "Coverage"
    url = "https://coverage.readthedocs.io/"
    description = COVERAGE_TEXT
    setup_cmd = COVERAGE_CODE
    config_syntax = "toml"

    def is_used(self, folder: folderinfo.FolderInfo):
        return (
            "coverage" in folder.pyproject.tool or (folder.path / ".coveragerc").exists()
        )

    def get_config(self, folder):
        text = folder.pyproject.get_section_text("tool", "coverage")
        if (path := (folder.path / ".coveragerc")).exists():
            return f"{text}\n{path.read_text()}"
        return text


class MkDocs(Tool):
    identifier = "mkdocs"
    title = "MkDocs"
    url = "https://mkdocs.org/"
    description = MKDOCS_TEXT
    setup_cmd = MKDOCS_CODE
    config_syntax = "yaml"

    def is_used(self, folder: folderinfo.FolderInfo):
        return bool(folder.mkdocs_config)

    def get_config(self, folder):
        return yamlhelpers.dump_yaml(folder.mkdocs_config)


class MkDocsMaterial(Tool):
    identifier = "mkdocs-material"
    title = "Material for MkDocs"
    url = "https://squidfunk.github.io/mkdocs-material/"
    description = MATERIAL_TEXT
    setup_cmd = None
    config_syntax = "yaml"

    def is_used(self, folder: folderinfo.FolderInfo):
        if (
            folder
            and folder.mkdocs_config
            and (theme := folder.mkdocs_config.get("theme"))
        ):
            return (
                theme == "material"
                if isinstance(theme, str)
                else theme.get("name") == "material"
            )
        return False

    def get_config(self, folder):
        return folder and yamlhelpers.dump_yaml(folder.mkdocs_config.get("theme"))


ToolStr = Literal[
    "pre-commit",
    "ruff",
    "mypy",
    "coverage",
    "mkdocs",
    "mkdocs-material",
    "black",
]


TOOLS: dict[ToolStr, Tool] = {
    p.identifier: p
    for p in [
        PreCommit(),
        Ruff(),
        Black(),
        MyPy(),
        Coverage(),
        MkDocs(),
        MkDocsMaterial(),
    ]
}

from __future__ import annotations

from mknodes.info import folderinfo
from mknodes.utils import pathhelpers, yamlhelpers


PRE_COMMIT_CODE = """
# Setup pre-commit hooks for required formatting
pre-commit install
"""

PRE_COMMIT_TEXT = """This project uses **pre-commit** to ensure code quality.
A `.pre-commit-config.yaml` configuration file tailored for this project is provided
in the root folder."""


MYPY_CODE = """
{{ metadata.build_system.run_prefix }}mypy --help
"""

MYPY_TEXT = """**MyPy** is used for type checking. You can find the configuration in the
`pyproject.toml` file."""

PYRIGHT_CODE = """
{{ metadata.build_system.run_prefix }}pyright --help
"""

PYRIGHT_TEXT = """**PyRight** is used for type checking. You can find the configuration in the
`pyproject.toml` file."""

RUFF_CODE = """
{{ metadata.build_system.run_prefix }}ruff --help
"""

RUFF_TEXT = """**Ruff** is used as a linter. You can find the configuration in the
`pyproject.toml` file."""

BLACK_CODE = """
{{ metadata.build_system.run_prefix }}black .
"""

BLACK_TEXT = """**Black** is used as a code formatter. You can find the configuration in
the `pyproject.toml` file."""

COVERAGE_CODE = """
{{ metadata.build_system.run_prefix }}coverage run some_module.py
"""

COVERAGE_TEXT = """**Coverage** is used to monitor test coverage."""

MKDOCS_CODE = """
# To build the docs
{{ metadata.build_system.run_prefix }}mkdocs build

# To serve the docs locally at http://127.0.0.1:8000/
{{ metadata.build_system.run_prefix }}mkdocs serve

# For additional mkdocs help and options:
{{ metadata.build_system.run_prefix }}mkdocs --help
"""

MKDOCS_TEXT = """**MkDocs** is used to create the documentation."""


MATERIAL_TEXT = """**Material for MkDocs** is used as the Website theme."""


class Tool:
    identifier: str
    title: str
    url: str
    description: str
    logo: str | None = None
    setup_cmd: str | None
    config_syntax: str
    pre_commit_repo: str | None = None

    def __init__(self, folderinfo):
        self.used = self.is_used(folderinfo)
        self.cfg = self.get_config(folderinfo) if self.used else None

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
    logo = "https://avatars.githubusercontent.com/u/6943086?s=200&v=4"
    description = PRE_COMMIT_TEXT
    setup_cmd = PRE_COMMIT_CODE
    config_syntax = "yaml"
    cfg_file = ".pre-commit-config.yaml"
    pre_commit_repo = "https://github.com/pre-commit/pre-commit-hooks"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return bool(pathhelpers.find_cfg_for_folder(self.cfg_file, folder.path))

    def get_config(self, folder):
        path = pathhelpers.find_cfg_for_folder(self.cfg_file, folder.path)
        return path.read_text(encoding="utf-8") if path else None


class Ruff(Tool):
    identifier = "ruff"
    title = "Ruff"
    url = "https://beta.ruff.rs/"
    logo = "https://docs.astral.sh/ruff/assets/bolt.svg"
    description = RUFF_TEXT
    setup_cmd = RUFF_CODE
    config_syntax = "toml"
    pre_commit_repo = "https://github.com/charliermarsh/ruff-pre-commit"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return "ruff" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "ruff")


class Black(Tool):
    identifier = "black"
    title = "Black"
    url = "https://github.com/psf/black"
    logo = (
        "https://raw.githubusercontent.com/psf/black/main/docs/_static/logo2-readme.png"
    )
    description = BLACK_TEXT
    setup_cmd = BLACK_CODE
    config_syntax = "toml"
    pre_commit_config = "https://github.com/psf/black-pre-commit-mirror"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return "black" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "black")


class MyPy(Tool):
    identifier = "mypy"
    title = "MyPy"
    logo = "https://github.com/python/mypy/raw/master/docs/source/mypy_light.svg"
    url = "https://mypy-lang.org"
    description = MYPY_TEXT
    setup_cmd = MYPY_CODE
    config_syntax = "toml"
    pre_commit_repo = "https://github.com/pre-commit/mirrors-mypy"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return "mypy" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "mypy")


class PyRight(Tool):
    identifier = "pyright"
    title = "PyRight"
    url = "https://microsoft.github.io/pyright/"
    logo = "https://github.com/microsoft/pyright/raw/main/docs/img/PyrightLarge.png"
    description = PYRIGHT_TEXT
    setup_cmd = PYRIGHT_CODE
    config_syntax = "toml"
    pre_commit_repo = "https://github.com/RobertCraigie/pyright-python"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return "pyright" in folder.pyproject.tool

    def get_config(self, folder):
        return folder.pyproject.get_section_text("tool", "pyright")


class Coverage(Tool):
    identifier = "coverage"
    title = "Coverage"
    url = "https://coverage.readthedocs.io/"
    logo = "https://coverage.readthedocs.io/en/7.3.2/_static/sleepy-snake-circle-150.png"
    description = COVERAGE_TEXT
    setup_cmd = COVERAGE_CODE
    config_syntax = "toml"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return (
            "coverage" in folder.pyproject.tool or (folder.path / ".coveragerc").exists()
        )

    def get_config(self, folder):
        text = folder.pyproject.get_section_text("tool", "coverage")
        if (path := (folder.path / ".coveragerc")).exists():
            return f"{text}\n{path.read_text(encoding='utf-8')}"
        return text


class MkDocs(Tool):
    identifier = "mkdocs"
    title = "MkDocs"
    logo = "https://avatars.githubusercontent.com/u/9692741?s=200&v=4"
    url = "https://mkdocs.org/"
    description = MKDOCS_TEXT
    setup_cmd = MKDOCS_CODE
    config_syntax = "yaml"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        return bool(folder.mkdocs_config)

    def get_config(self, folder):
        return folder.mkdocs_config.serialize("yaml")


class MkDocsMaterial(Tool):
    identifier = "mkdocs-material"
    title = "Material for MkDocs"
    logo = "https://raw.githubusercontent.com/squidfunk/mkdocs-material/master/.github/assets/logo.svg"
    url = "https://squidfunk.github.io/mkdocs-material/"
    description = MATERIAL_TEXT
    setup_cmd = None
    config_syntax = "yaml"

    def is_used(self, folder: folderinfo.FolderInfo) -> bool:
        if folder and (cfg := folder.mkdocs_config):
            return cfg.theme_name == "material"
        return False

    def get_config(self, folder):
        return folder and yamlhelpers.dump_yaml(folder.mkdocs_config.get("theme"))


TOOLS: dict[str, type[Tool]] = {
    p.identifier: p
    for p in [
        PreCommit,
        Ruff,
        Black,
        PyRight,
        MyPy,
        Coverage,
        MkDocs,
        MkDocsMaterial,
    ]
}

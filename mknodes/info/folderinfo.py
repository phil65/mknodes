from __future__ import annotations

import importlib
import logging
import os
import pathlib
import re

from mknodes.data import taskrunners, tools
from mknodes.info import gitrepository, packageinfo, pyproject
from mknodes.utils import helpers, reprhelpers


logger = logging.getLogger(__name__)


GITHUB_REGEX = re.compile(
    r"(?:http?:\/\/|https?:\/\/)?"
    r"(?:www\.)?"
    r"github\.com\/"
    r"(?:\/*)"
    r"([\w\-\.]*)\/"
    r"([\w\-]*)"
    r"(?:\/|$)?"  # noqa: COM812
)


class FolderInfo:
    """Aggregates information about a working dir."""

    def __init__(self, path: str | os.PathLike | None = None):
        self.path = pathlib.Path(path or ".")
        self.pyproject = pyproject.PyProject(self.path)
        self.git = gitrepository.GitRepository(self.path)
        text = (self.path / "mkdocs.yml").read_text(encoding="utf-8")
        self.mkdocs_config = helpers.load_yaml(text, mode="unsafe")
        mod_name = self.git.remotes.origin.url.split(".git")[0].split("/")[-1]
        self.module = importlib.import_module(mod_name)

    def __repr__(self):
        return reprhelpers.get_repr(self, path=self.path)

    @classmethod
    def clone_from(
        cls,
        url: str,
        # path: str | os.PathLike,
        depth: int = 100,
    ):
        import tempfile

        import git

        directory = tempfile.TemporaryDirectory(prefix="mknodes_repo_")
        repo = git.Repo.clone_from(url, directory.name, depth=depth)
        kls = cls(repo.working_dir)
        kls._temp_directory = directory
        return kls

    @property
    def info(self):
        return packageinfo.get_info(self.pyproject.name)

    @property
    def repository_url(self) -> str | None:
        return (
            url
            if (url := self.mkdocs_config.get("repo_url"))
            else self.info.repository_url
        )

    @property
    def repository_username(self) -> str | None:
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(1)
        return None

    @property
    def repository_name(self) -> str | None:
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(2)
        return None

    @property
    def package_name(self):
        return self.module.__name__

    @property
    def package_repos(self):
        return self.pyproject.package_repos

    @property
    def commit_types(self):
        return self.pyproject.allowed_commit_types

    @property
    def tools(self) -> list[tools.Tool]:
        """Return a list of build tools used by this package."""
        return [t for t in tools.TOOLS.values() if t.is_used(self)]

    def aggregate_info(self) -> dict:
        infos = dict(
            repository_name=self.repository_name,
            repository_username=self.repository_username,
            repository_url=self.repository_url,
        )
        return infos | self.info.metadata.json

    @property
    def task_runners(self) -> list[taskrunners.TaskRunner]:
        """Return list of task runners used by this package."""
        return [
            runner
            for runner in taskrunners.TASK_RUNNERS.values()
            if any(
                helpers.find_file_in_folder_or_parent(i, self.path)
                for i in runner.filenames
            )
        ]


if __name__ == "__main__":
    info = FolderInfo.clone_from("https://github.com/mkdocs/mkdocs.git")
    print(info)

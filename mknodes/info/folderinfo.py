from __future__ import annotations

import logging
import os
import pathlib

from mknodes.data import taskrunners, tools
from mknodes.info import gitrepository, pyproject
from mknodes.utils import helpers, reprhelpers


logger = logging.getLogger(__name__)


class FolderInfo:
    """Aggregates information about a working dir."""

    def __init__(self, path: str | os.PathLike | None = None):
        self.path = pathlib.Path(path or ".")
        self.pyproject = pyproject.PyProject(self.path)
        self.git = gitrepository.GitRepository(self.path)
        text = (self.path / "mkdocs.yml").read_text()
        self.mkdocs_config = helpers.load_yaml(text)

    def __repr__(self):
        return reprhelpers.get_repr(self, path=self.path)

    @classmethod
    def clone_from(
        cls,
        url: str,
        # path: str | os.PathLike,
        depth: int = 1,
    ):
        import tempfile

        import git

        directory = tempfile.TemporaryDirectory(prefix="mknodes_repo_")
        repo = git.Repo.clone_from(url, directory.name, depth=depth)
        kls = cls(repo.working_dir)
        kls._temp_directory = directory
        return kls

    @property
    def package_repos(self):
        return self.pyproject.package_repos

    @property
    def commit_types(self):
        return self.pyproject.allowed_commit_types

    @property
    def tools(self) -> list[tools.Tool]:
        """Return a list of build tools used by this package."""
        return [t for t in tools.TOOLS.values() if t.is_used(self.path)]

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
    info = FolderInfo.clone_from("https://github.com/mkdocstrings/mkdocstrings.git")
    print(info.mkdocs_config)

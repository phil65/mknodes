from __future__ import annotations

import logging
import os

from mknodes.data import taskrunners, tools
from mknodes.info import gitrepository, pyproject
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class FolderInfo:
    """Aggregates information about a working dir."""

    def __init__(self, path: str | os.PathLike | None = None):
        self.path = path or "."
        self.pyproject = pyproject.PyProject(path)
        self.git = gitrepository.GitRepository(self.path)

    def __repr__(self):
        return helpers.get_repr(self, path=self.path)

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
    project = FolderInfo()
    bs = project.task_runners
    print(bs)

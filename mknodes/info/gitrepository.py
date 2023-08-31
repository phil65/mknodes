from __future__ import annotations

from functools import cached_property
import logging

import git


logger = logging.getLogger(__name__)


class GitRepository(git.Repo):
    """Aggregates information about a git repo."""

    @cached_property
    def main_branch(self) -> str:
        has_main_branch = any(branch.name == "main" for branch in self.branches)
        return "main" if has_main_branch else "master"

    def get_last_commits(self, num: int):
        return list(self.iter_commits(self.main_branch, max_count=num))


if __name__ == "__main__":
    repo = GitRepository(".")
    print(repo.main_branch)

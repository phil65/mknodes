from __future__ import annotations

from functools import cached_property
from typing import Self
from urllib import parse

import git

from mknodes.info import contexts
from mknodes.utils import log


logger = log.get_logger(__name__)


class GitRepository(git.Repo):
    """Aggregates information about a git repo."""

    @cached_property
    def main_branch(self) -> str:
        has_main_branch = any(branch.name == "main" for branch in self.heads)
        return "main" if has_main_branch else "master"

    @classmethod
    def clone_from(cls, *args, **kwargs) -> Self:
        return super().clone_from(*args, **kwargs)  # type: ignore[return-value]

    @cached_property
    def repo_name(self) -> str:
        return self.remotes.origin.url.split(".git")[0].split("/")[-1]

    @cached_property
    def repo_url(self) -> str:
        return self.remotes.origin.url.split(".git")[0] + "/"

    def get_last_commits(
        self,
        num: int,
        branch: str | None = None,
    ) -> list[git.Commit]:  # type: ignore[name-defined]
        """Return last x commits.

        Arguments:
            num: Amount of commits to fetch.
            branch: Branch to get commits from. Defaults to main / master.
        """
        return list(self.iter_commits(branch or self.main_branch, max_count=num))

    @cached_property
    def code_repository(self) -> str:
        repo_host = parse.urlsplit(self.remotes.origin.url).netloc.lower()
        match repo_host:
            case "github.com":
                return "GitHub"
            case "bitbucket.org":
                return "Bitbucket"
            case "gitlab.com":
                return "GitLab"
            case _:
                return repo_host.split(".")[0].title()

    @cached_property
    def context(self):
        return contexts.GitContext(
            main_branch=self.main_branch,
            repo_hoster=self.code_repository,
            last_commits=self.get_last_commits(100),
            repo_name=self.repo_name,
        )


if __name__ == "__main__":
    repo = GitRepository(".")
    print(repo.repo_url)

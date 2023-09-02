from __future__ import annotations

from functools import cached_property
import logging

from urllib import parse

import git


logger = logging.getLogger(__name__)


class GitRepository(git.Repo):
    """Aggregates information about a git repo."""

    @cached_property
    def main_branch(self) -> str:
        has_main_branch = any(branch.name == "main" for branch in self.branches)
        return "main" if has_main_branch else "master"

    def get_repo_name(self) -> str:
        return self.remotes.origin.url.split(".git")[0].split("/")[-1]

    def get_last_commits(self, num: int):
        return list(self.iter_commits(self.main_branch, max_count=num))

    def get_code_repository(self) -> str:
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


if __name__ == "__main__":
    repo = GitRepository(".")
    print(repo.get_code_repository())

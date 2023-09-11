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
        hast_master_branch = any(branch.name == "master" for branch in self.heads)
        return "master" if hast_master_branch else "main"

    @classmethod
    def clone_from(cls, *args, **kwargs) -> Self:
        """Clone a repository. Overriden for typing."""
        return super().clone_from(*args, **kwargs)  # type: ignore[return-value]

    @cached_property
    def repo_name(self) -> str:
        """Name (aka the last part of the url) of the Git repository."""
        return self.remotes.origin.url.split(".git")[0].split("/")[-1]

    @cached_property
    def repo_url(self) -> str:
        """Url of the remote repository (without .git)."""
        return self.remotes.origin.url.split(".git")[0] + "/"

    @cached_property
    def commit_to_tag(self) -> dict[git.Commit, str]:  # type: ignore[name-defined]
        """Dictionary mapping git.Commits to tag strings."""
        return {self.commit(i.commit): i.name for i in self.tags}

    def get_version_for_commit(
        self,
        commit: git.Commit | str,  # type: ignore[name-defined]
    ) -> str | None:
        """Iterate commit parents to find the associated version of the commit."""
        if isinstance(commit, str):
            commit = self.commit(commit)
        return next(
            (
                self.commit_to_tag[c]
                for c in [commit, *commit.parents]
                if c in self.commit_to_tag
            ),
            None,
        )

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
        rev = branch or self.main_branch
        try:
            return list(self.iter_commits(rev, max_count=num))
        except git.exc.GitCommandError:  # type: ignore[name-defined]
            logger.warning("Could not fetch commits for %r", rev)
            return []

    @cached_property
    def code_repository(self) -> str:
        """Get the remote code repository name (like "GitHub")."""
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
    def context(self) -> contexts.GitContext:
        return contexts.GitContext(
            main_branch=self.main_branch,
            repo_hoster=self.code_repository,
            last_commits=self.get_last_commits(100),
            repo_name=self.repo_name,
        )


if __name__ == "__main__":
    repo = GitRepository(".")
    # for commit in repo.get_last_commits(100):
    v = repo.get_version_for_commit("949f6df9cdf49d175bfe2c57d8f51d3882c7fc01")
    print(v)

from __future__ import annotations

from functools import cached_property
import os
import tempfile

from typing import Any, Self
from urllib import parse

import git

from mknodes.info import contexts
from mknodes.utils import helpers, log


logger = log.get_logger(__name__)


class GitRepository(git.Repo):
    """Aggregates information about a git repo."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # to keep a reference to a TempDirectory instance
        self.temp_directory: tempfile.TemporaryDirectory | None = None

    def __len__(self):
        return len(list(self.iter_commits("HEAD")))

    @cached_property
    def main_branch(self) -> str:
        """The default branch of the repository."""
        has_master_branch = any(branch.name == "master" for branch in self.heads)
        return "master" if has_master_branch else "main"

    @classmethod
    def clone_from(  # type: ignore[override]
        cls,
        url: os.PathLike | str,
        to_path: os.PathLike | str,
        depth: int | None = None,
        **kwargs: Any,
    ) -> Self:
        """Clone a repository. Overridden for typing.

        Arguments:
            url: The repository URL
            to_path: the path to clone to
            depth: Clone depth (Amount of commits to fetch)
            kwargs: Further arguments passed to `git clone`
        """
        if depth is not None:
            kwargs["depth"] = depth
        return super().clone_from(url, to_path, **kwargs)  # type: ignore[return-value]

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
        return {
            self.commit(i.commit): i.name
            for i in sorted(self.tags, key=lambda x: x.commit.committed_date)
        }

    def get_version_for_commit(
        self,
        commit: git.Commit | str,  # type: ignore[name-defined]
    ) -> str | None:
        """Iterate commit parents to find the associated version of the commit.

        Arguments:
            commit: Commit to get a version for.
        """
        if isinstance(commit, str):
            commit = self.commit(commit)
        mapping = self.commit_to_tag
        try:
            return next((mapping[c] for c in commit.traverse() if c in mapping), None)
        except ValueError:
            msg = f"Could not get version for {commit}"
            logger.exception(msg)
            return None

    @cached_property
    def version_changes(self) -> dict[str, dict[str, list[git.Commit]]]:  # type: ignore[name-defined]
        """Returns a nested dictionary of commits, grouped by version and commit type.

        Shape of retuned dict:
        {"v0.x.x": {"feat": [git.Commit, ...], ...}, ...}
        """
        commits = [
            i
            for i in self.get_last_commits()
            if self.get_version_for_commit(i) and i not in self.commit_to_tag
        ]
        groups = helpers.groupby(commits, self.get_version_for_commit, natural_sort=True)
        return {
            k: helpers.groupby(v, lambda x: x.message.split(":")[0])
            for k, v in groups.items()
        }

    def get_last_commits(
        self,
        num: int | None = None,
        branch: str | None = None,
    ) -> list[git.Commit]:  # type: ignore[name-defined]
        """Return last x commits.

        Arguments:
            num: Amount of commits to fetch.
            branch: Branch to get commits from. Defaults to main / master.
        """
        rev = branch or self.main_branch
        try:
            kwargs = {} if not num else {"max_count": str(num)}
            return list(self.iter_commits(rev, **kwargs))
        except git.exc.GitCommandError:  # type: ignore[name-defined]
            logger.warning("Could not fetch commits for %r", rev)
            return []

    @cached_property
    def code_repository(self) -> str:
        """Get the remote code repository name (like "GitHub")."""
        match parse.urlsplit(self.remotes.origin.url).netloc.lower():
            case "github.com":
                return "GitHub"
            case "bitbucket.org":
                return "Bitbucket"
            case "gitlab.com":
                return "GitLab"
            case _ as repo_host:
                return repo_host.split(".")[0].title()

    @property
    def edit_uri(self) -> str | None:
        """The URL part needed to get to the edit page of the code hoster."""
        match parse.urlsplit(self.remotes.origin.url).netloc.lower():
            case "github.com" | "gitlab.com":
                return f"edit/{self.main_branch}/"
            case "bitbucket.org":
                return "src/default/"
            case _:
                return None

    @cached_property
    def context(self) -> contexts.GitContext:
        """Return Git context."""
        return contexts.GitContext(
            main_branch=self.main_branch,
            repo_hoster=self.code_repository,
            last_commits=self.get_last_commits(100),
            repo_name=self.repo_name,
            edit_uri=self.edit_uri,
            current_sha=self.head.object.hexsha,
            current_committer=self.head.object.committer,
            current_date_committed=self.head.object.committed_datetime,
            current_author=self.head.object.author,
            current_date_authored=self.head.object.authored_datetime,
            last_version=self.get_version_for_commit("HEAD"),
        )


if __name__ == "__main__":
    repo = GitRepository(".")
    # for commit in repo.get_last_commits(100):
    v = repo.get_version_for_commit("949f6df9cdf49d175bfe2c57d8f51d3882c7fc01")
    print(v)

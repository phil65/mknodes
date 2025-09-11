from __future__ import annotations

import functools
from typing import TYPE_CHECKING, Any, Self

import git
from jinjarope import iterfilters

from mknodes.info import contexts
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    import os
    import tempfile


logger = log.get_logger(__name__)


class CommitList(list[git.Commit]):
    def __repr__(self):
        return reprhelpers.limit_repr.repr(list(self))


class GitRepository(git.Repo):
    """Aggregates information about a git repo."""

    def __init__(self, path: str | os.PathLike[str] | None = None, **kwargs: Any):
        import githarbor
        from githarbor.core.proxy import Repository

        super().__init__(path or ".", **kwargs)
        # to keep a reference to a TempDirectory instance
        self.temp_directory: tempfile.TemporaryDirectory[str] | None = None
        try:
            self.remote_repo = githarbor.create_repository(self.remotes.origin.url)
        except Exception:  # noqa: BLE001
            self.remote_repo = Repository(githarbor.BaseRepository())

    def __len__(self):
        return len(list(self.iter_commits("HEAD")))

    @functools.cached_property
    def main_branch(self) -> str:
        """The default branch of the repository."""
        has_master_branch = any(branch.name == "master" for branch in self.heads)
        return "master" if has_master_branch else "main"

    @classmethod
    def clone_from(  # type: ignore[override]  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        url: os.PathLike[str] | str,
        to_path: os.PathLike[str] | str,
        depth: int | None = None,
        **kwargs: Any,
    ) -> Self:
        """Clone a repository. Overridden for typing.

        Args:
            url: The repository URL
            to_path: the path to clone to
            depth: Clone depth (Amount of commits to fetch)
            kwargs: Further arguments passed to `git clone`
        """
        if depth is not None:
            kwargs["depth"] = depth
        return super().clone_from(url, to_path, **kwargs)  # type: ignore[return-value]  # pyright: ignore[reportReturnType]

    @functools.cached_property
    def repo_name(self) -> str:
        """Name (aka the last part of the url) of the Git repository."""
        return self.remotes.origin.url.split(".git")[0].split("/")[-1]

    @functools.cached_property
    def repo_url(self) -> str:
        """Url of the remote repository (without .git)."""
        return self.remotes.origin.url.split(".git")[0] + "/"

    @functools.cached_property
    def commit_to_tag(self) -> dict[git.Commit, str]:  # type: ignore[name-defined]
        """Dictionary mapping git.Commits to tag strings."""
        return {
            self.commit(i.commit): i.name
            for i in sorted(self.tags, key=lambda x: x.commit.committed_date)
        }

    def get_commit(self, commit: str) -> git.Commit | None:  # type: ignore[name-defined]
        import gitdb.exc

        try:
            return self.commit(commit)
        except gitdb.exc.BadName:
            return None

    def get_version_for_commit(
        self,
        commit: git.Commit | str,  # type: ignore[name-defined]
    ) -> str | None:
        """Iterate commit parents to find the associated version of the commit.

        Args:
            commit: Commit to get a version for.
        """
        commit_obj = self.get_commit(commit) if isinstance(commit, str) else commit
        if commit_obj is None:
            return None
        mapping = self.commit_to_tag
        if commit_obj in mapping:
            return mapping[commit_obj]
        try:
            idx = self.all_commits.index(commit_obj)
            all_commits = list(reversed(self.all_commits[:idx]))
            return next((mapping[c] for c in all_commits if c in mapping), None)
        except ValueError:
            msg = f"Could not get version for {commit_obj}"
            logger.exception(msg)
            return None

    @functools.cached_property
    def version_changes(self) -> dict[str, dict[str, list[git.Commit]]]:  # type: ignore[name-defined]
        """Returns a nested dictionary of commits, grouped by version and commit type.

        Shape of retuned dict:
        {"v0.x.x": {"feat": [git.Commit, ...], ...}, ...}
        """
        commits = [i for i in self.all_commits if i not in self.commit_to_tag]
        groups = iterfilters.groupby(
            commits, self.get_version_for_commit, natural_sort=True
        )

        def get_commit_group(commit: git.Commit) -> str:
            assert isinstance(commit.message, str)
            return commit.message.split(":")[0]

        return {k: iterfilters.groupby(v, get_commit_group) for k, v in groups.items()}

    @functools.cached_property
    def all_commits(self) -> list[git.Commit]:  # type: ignore[name-defined]
        return self.get_commits()

    def get_commits(
        self,
        num: int | None = None,
        branch: str | None = None,
    ) -> list[git.Commit]:  # type: ignore[name-defined]
        """Return last x commits.

        Args:
            num: Amount of commits to fetch.
            branch: Branch to get commits from. Defaults to main / master.
        """
        rev = branch or self.main_branch
        try:
            kwargs = {} if not num else {"max_count": str(num)}
            return CommitList(self.iter_commits(rev, **kwargs))
        except git.GitCommandError:
            logger.warning("Could not fetch commits for %r", rev)
            return CommitList()

    @functools.cached_property
    def code_repository(self) -> str:
        """Get the remote code repository name (like "GitHub")."""
        return self.remote_repo.repository_type

    @property
    def edit_uri(self) -> str | None:
        """The URL part needed to get to the edit page of the code hoster."""
        return self.remote_repo.edit_base_uri

    @functools.cached_property
    def context(self) -> contexts.GitContext:
        """Return Git context."""
        return contexts.GitContext(
            main_branch=self.main_branch,
            repo_hoster=self.code_repository,
            commits=self.all_commits,
            repo_name=self.repo_name,
            edit_uri=self.edit_uri,
            current_sha=self.head.object.hexsha,
            current_committer=self.head.object.committer.name
            if isinstance(self.head.object.committer.name, str)
            else "",
            # current_committer_mail=self.head.object.committer.email,
            current_date_committed=self.head.object.committed_datetime,
            current_author=self.head.object.author.name
            if isinstance(self.head.object.author.name, str)
            else "",
            # current_author_email=self.head.object.author.email,
            current_date_authored=self.head.object.authored_datetime,
            last_version=self.get_version_for_commit("HEAD"),
        )


if __name__ == "__main__":
    repo = GitRepository(".")
    # for commit in repo.get_commits(100):
    v = repo.get_version_for_commit("949f6df9cdf49d175bfe2c57d8f51d3882c7fc01")
    print(v)

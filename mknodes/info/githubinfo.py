from __future__ import annotations

import datetime
import functools
import os

import github

from github import Commit

from mknodes.info import contexts
from mknodes.utils import downloadhelpers, log, pathhelpers, reprhelpers


RAW_URL = "https://raw.githubusercontent.com/"
TOKEN = os.environ.get("GITHUB_TOKEN")

auth = github.Auth.Token(TOKEN) if TOKEN else None


logger = log.get_logger(__name__)


class GitHubRepo:
    def __init__(self, username: str, repository: str):
        """Constructor.

        Arguments:
            username: Github user name
            repository: Github repository / project name
        """
        self.main = github.Github(auth=auth)
        self.username = username
        self.repo_name = repository
        self.user: github.NamedUser.NamedUser = self.main.get_user(username)  # type: ignore
        self.repo = self.main.get_repo(f"{username}/{repository}")
        self.default_branch = self.repo.default_branch

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            username=self.username,
            repository=self.repo_name,
        )

    def download_from_path(
        self,
        path: str | os.PathLike,
        destination: str | os.PathLike,
        recursive: bool = False,
    ):
        """Download a file from this github repository.

        Arguments:
            path: Path to the file we want to download.
            destination: Path where file should be saved.
            recursive: Download all files from a folder (and subfolders).
        """
        user_name = self.main.get_user().login if TOKEN else None
        return pathhelpers.download_from_github(
            org=self.username,
            repo=self.repo_name,
            path=path,
            destination=destination,
            username=user_name,
            token=TOKEN,
            recursive=recursive,
        )

    @functools.cached_property
    def workflows(self) -> list[dict[str, str]]:
        """Return a list of dictionaries containing info about the current workflows."""
        result = []
        for wf in self.repo.get_workflows():
            url = f"{self.raw_prefix}{self.default_branch}/{wf.path}"
            data = downloadhelpers.download(url)
            item = dict(name=wf.name, workflow=data.decode(), badge_url=wf.badge_url)
            result.append(item)
        return result

    @functools.cached_property
    def raw_prefix(self) -> str:
        """Path to the base url of the "Raw" links of GitHub.

        If used in combination with the relative path of a module file,
        this geives a valid link to a GitHub raw link.
        """
        return f"{RAW_URL}{self.username}/{self.repo_name}/"

    def get_last_commits(
        self,
        branch: str | None = None,
        since: datetime.datetime | None = None,
    ) -> list[Commit.Commit]:  # type: ignore[valid-type]
        """Return last x commits.

        Arguments:
            since: Amount of commits to fetch.
            branch: Branch to get commits from. Defaults to main / master.
        """
        rev = branch or self.default_branch
        kwargs = dict(since=since) if since else {}
        return self.repo.get_commits(rev, **kwargs)  # type: ignore

    @functools.cached_property
    def context(self) -> contexts.GitHubContext:
        """Return github context."""
        return contexts.GitHubContext(
            default_branch=self.default_branch,
            repo_name=self.repo_name,
            workflows=self.workflows,
            avatar_url=self.user.avatar_url,
            bio=self.user.bio,
            blog=self.user.blog,
            company=self.user.company,
            # contributions=self.user.contributions,
            email=self.user.email,
            followers=self.user.followers,
            gravatar_id=self.user.gravatar_id,
            hireable=self.user.hireable,
            location=self.user.location,
            name=self.user.name,
            twitter_username=self.user.twitter_username,
        )


if __name__ == "__main__":
    g = GitHubRepo("phil65", "mknodes")
    node = g.main.get_user()

from __future__ import annotations

import functools
import os

import github

from mknodes.info import contexts
from mknodes.utils import cache, log


RAW_URL = "https://raw.githubusercontent.com/"

token = os.environ.get("GITHUB_ACCESS_TOKEN")
auth = github.Auth.Token(token) if token else None


logger = log.get_logger(__name__)


class GitHubRepo:
    def __init__(self, username: str, repository: str):
        self.main = github.Github(auth=auth)
        self.username = username
        self.repo_name = repository
        self.user = self.main.search_users(username)[0]
        self.repo = self.main.get_repo(f"{username}/{repository}")
        self.default_branch = self.repo.default_branch

    @functools.cached_property
    def workflows(self):
        result = []
        for wf in self.repo.get_workflows():
            url = f"{self.raw_prefix}{self.default_branch}/{wf.path}"
            data = cache.download_and_cache_url(url)
            item = dict(name=wf.name, workflow=data.decode(), badge_url=wf.badge_url)
            result.append(item)
        return result

    @functools.cached_property
    def raw_prefix(self):
        return f"{RAW_URL}{self.username}/{self.repo_name}/"

    @functools.cached_property
    def context(self):
        return contexts.GitHubContext(
            default_branch=self.default_branch,
            repo_name=self.repo_name,
            workflows=self.workflows,
            avatar_url=self.user.avatar_url,
            bio=self.user.bio,
            blog=self.user.blog,
            company=self.user.company,
            contributions=self.user.contributions,
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
    print(g)

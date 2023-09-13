from __future__ import annotations

import dataclasses
import datetime
import json
import os

import dateutil.parser

from mknodes.theme import mkblog
from mknodes.utils import cache


@dataclasses.dataclass(frozen=True)
class Commit:
    sha: str
    author_name: str
    author_email: str
    author_date: datetime.datetime
    author_avatar: str
    author_url: str
    author_login: str
    committer_name: str
    committer_email: str
    committer_date: datetime.datetime
    committer_avatar: str
    committer_url: str
    committer_login: str
    html_url: str
    message: str
    verified: str
    verified_reason: str


def get_latest_commits(owner: str, repo: str, page: int = 1):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}"
    response = cache.download_and_cache_url(url)
    commits = json.loads(response.decode())
    return [
        Commit(
            sha=dct["commit"]["tree"]["sha"],
            author_name=dct["commit"]["author"]["name"],
            author_email=dct["commit"]["author"]["email"],
            author_date=dateutil.parser.parse(dct["commit"]["author"]["date"]),
            author_avatar=dct["author"]["avatar_url"],
            author_login=dct["author"]["login"],
            author_url=dct["author"]["html_url"],
            committer_name=dct["commit"]["committer"]["name"],
            committer_email=dct["commit"]["committer"]["email"],
            committer_date=dateutil.parser.parse(dct["commit"]["committer"]["date"]),
            committer_avatar=dct["committer"]["avatar_url"],
            committer_login=dct["committer"]["login"],
            committer_url=dct["committer"]["html_url"],
            html_url=dct["html_url"],
            message=dct["commit"]["message"],
            verified=dct["commit"]["verification"]["verified"],
            verified_reason=dct["commit"]["verification"]["reason"],
        )
        for dct in commits
    ]


class MkGitBlog(mkblog.MkBlog):
    def __init__(self, org: str, repo: str, posts_dir: str | os.PathLike, **kwargs):
        super().__init__(**kwargs)
        self.commits: list[mkblog.MkBlogPost] = []
        self.posts_dir = posts_dir
        self.org = org
        self.repo = repo

    def add_commits(self):
        commits = get_latest_commits(self.org, self.repo)
        for c in commits:
            if c.author_login not in self.authors:
                self.authors[c.author_login] = mkblog.Author(
                    name=c.author_login,
                    description=c.author_email,
                    avatar=c.author_avatar,
                )
            self.add_post(
                date=c.author_date,
                authors=list({c.author_name, c.committer_name}),
                text=c.message,
                draft=False,
                path=f"{c.sha}.md",
            )


if __name__ == "__main__":
    blog = MkGitBlog("phil65", "mknodes", "blog/posts")
    blog.add_commits()
    page = blog.pages[1]

    print(page)
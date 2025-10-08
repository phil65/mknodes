from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any

import dateutil.parser

from mknodes.theme import mkblog
from mknodes.utils import downloadhelpers


if TYPE_CHECKING:
    import datetime
    import os


@dataclasses.dataclass(frozen=True)
class Commit:
    """Class representing a single Git commit."""

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


async def get_latest_commits(owner: str, repo: str, page: int = 1) -> list[Commit]:
    """Return latest commits from given repository.

    Args:
        owner: Repository owner
        repo: Repository name
        page: page to get. Each page contains max 100 commits.
    """
    import anyenv

    url = f"https://api.github.com/repos/{owner}/{repo}/commits?per_page=100&page={page}"
    response = await downloadhelpers.download_async(url)
    commits = anyenv.load_json(response.decode(), return_type=list)
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
    """The MkDocs-Material plugin-blog, misused as a Git log."""

    def __init__(
        self,
        org: str,
        repo: str,
        posts_dir: str | os.PathLike[str],
        **kwargs: Any,
    ):
        """Instanciate a MkGitBlog.

        Args:
            org: The repository org
            repo: The repository name
            posts_dir: The folder of the post files
            kwargs: Additional keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.commits: list[mkblog.MkBlogPost] = []
        self.posts_dir = posts_dir
        self.org = org
        self.repo = repo

    async def add_commits(self):
        """Fetch commits and add them to the blog."""
        commits = await get_latest_commits(self.org, self.repo)
        for c in commits:
            if c.author_login not in self.authors:
                self.authors[c.author_login] = mkblog.Author(
                    name=c.author_login,
                    description=c.author_email,
                    avatar=c.author_avatar,
                )
            if c.committer_login not in self.authors:
                self.authors[c.committer_login] = mkblog.Author(
                    name=c.committer_login,
                    description=c.committer_email,
                    avatar=c.committer_avatar,
                )
            self.add_post(
                title=c.message,
                date=c.author_date,
                authors=list({c.author_login, c.committer_login}),
                text=c.message,
                draft=False,
                path=f"{c.sha[6:]}.md",
            )


if __name__ == "__main__":
    blog = MkGitBlog("phil65", "mknodes", "blog/posts")

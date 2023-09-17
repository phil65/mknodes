from __future__ import annotations

import dataclasses
import datetime

from mknodes.basenodes import mktext
from mknodes.info import yamlfile
from mknodes.navs import mknav
from mknodes.pages import metadata, mkpage


@dataclasses.dataclass(frozen=True)
class Author:
    """A blog post author."""

    name: str
    description: str | None = None
    avatar: str | None = None


@dataclasses.dataclass
class BlogMetadata(metadata.Metadata):
    """Extended Metadata class for blog posts."""

    date: str = ""
    draft: bool = True
    categories: list[str] = dataclasses.field(default_factory=list)
    authors: list[str] = dataclasses.field(default_factory=list)

    def as_dict(self):
        dct = super().as_dict()
        dct["date"] = self.date
        dct["draft"] = self.draft
        dct["categories"] = self.categories
        dct["authors"] = self.authors
        return dct


class MkBlog(mknav.MkNav):
    """Class representing the blog provided by the MkDocs-Material blog plugin."""

    def __init__(self, section: str | None = "Blog", **kwargs):
        super().__init__(section=section, **kwargs)
        self.authors: dict[str, Author] = {}

    def add_author(
        self,
        username: str,
        name: str,
        description: str | None = None,
        avatar: str | None = None,
    ):
        """Add an author to the blog.

        Authors get linked to the blog post authors to show extended information.

        Arguments:
            username: Username / slug of the author
            name: Full name of the author
            description: Short description of the author
            avatar: Url to an image used as avatar
        """
        author = Author(name=name, description=description, avatar=avatar)
        self.authors[username] = author

    def write_authors_yml(self):
        """Write the authors yaml file to disk."""
        authors_file = yamlfile.YamlFile()
        authors_file._data = {k: dataclasses.asdict(v) for k, v in self.authors.items()}
        # authors_file.write("docs/blog/.authors.yml", mode="yaml")
        self.add_file("blog/.authors.yml", authors_file.serialize("yaml"))
        self.add_file(".authors.yml", authors_file.serialize("yaml"))
        self.add_file("blog/authors.yml", authors_file.serialize("yaml"))
        self.add_file("authors.yml", authors_file.serialize("yaml"))

    def add_post(
        self,
        text: str,
        date: datetime.datetime | str,
        more_text: str | None = None,
        *,
        categories: list[str] | str | None = None,
        authors: list[str] | str | None = None,
        draft: bool = False,
        **kwargs,
    ):
        """Add a post to the blog.

        Arguments:
            text: Blog post text
            date: Time/Date of the post
            more_text: Text hidden behint the more button.
            categories: A list of categories this post is linked to
            authors: A list of authors of the post
            draft: Whether post is a draft
            kwargs: Keyword arguments passed to parent
        """
        page = MkBlogPost(
            date=date,
            draft=draft,
            categories=categories,
            authors=authors,
            **kwargs,
        )
        page += mktext.MkText(text)
        if more_text:
            page += "\n\n<!-- more -->\n\n"
            page += more_text
        self += page


class MkBlogPost(mkpage.MkPage):
    """Class representing a MkDocs-Material blog post."""

    DATE_FORMAT = "%Y-%m-%d"

    def __init__(
        self,
        date: str | datetime.datetime,
        *,
        draft: bool = True,
        categories: list[str] | str | None = None,
        authors: list[str] | str | None = None,
        **kwargs,
    ):
        """Constructor.

        Arguments:
            date: Time/Date of the post
            draft: Whether post is a draft
            categories: A list of categories this post is linked to
            authors: A list of authors of the post
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        if isinstance(authors, str):
            authors = [authors]
        if isinstance(categories, str):
            categories = [categories]
        self.metadata = BlogMetadata(
            **dataclasses.asdict(self.metadata),
            date=(
                date
                if isinstance(date, str)
                else datetime.datetime.strftime(date, self.DATE_FORMAT)
            ),
            draft=draft,
            categories=categories or [],
            authors=authors or [],
        )
        self.posts = mknav.MkNav("posts", parent=self)
        self.index_page = mkpage.MkPage()


if __name__ == "__main__":
    blog = MkBlog()
    blog.add_post("Hello", "2020-01-01", "more")
    page = blog.nav.pages[0]
    print(page.metadata)
    print(blog)

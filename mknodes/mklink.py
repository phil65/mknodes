from __future__ import annotations

import logging

from typing import Any

from mknodes import mknav, mknode, mkpage, project
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link."""

    def __init__(
        self,
        target: str | mkpage.MkPage | mknav.MkNav,
        title: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: Link target
            title: Title used for link
            kwargs: keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target
        self.title = title

    def __repr__(self):
        return helpers.get_repr(self, target=self.target, title=self.title)

    def _to_markdown(self) -> str:
        match self.target:
            case mkpage.MkPage():
                path = self.target.resolved_file_path.replace(".md", ".html")
                url = project.Project().config.site_url + path
            case mknav.MkNav():
                if self.target.index_page:
                    path = self.target.index_page.resolved_file_path
                    path = path.replace(".md", ".html")
                else:
                    path = self.target.resolved_file_path
                url = project.Project().config.site_url + path
            case str() if self.target.startswith(("http:", "https:", "www.")):
                url = self.target
            case str():
                url = f"{self.target}.md"
            case _:
                raise TypeError(self.target)
        title = self.target if self.title is None else self.title
        return f"[{title}]({url})"


if __name__ == "__main__":
    link = MkLink("www.test.de")

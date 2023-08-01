from __future__ import annotations

import logging

from typing import Any

from mknodes import mknav, mkpage, project
from mknodes.basenodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkLink(mknode.MkNode):
    """A simple Link."""

    ICON = "octicons/link-24"
    REQUIRED_EXTENSIONS = ["attr_list"]  # for buttons

    def __init__(
        self,
        target: str | mkpage.MkPage | mknav.MkNav,
        title: str | None = None,
        as_button: bool = False,
        primary_color: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: Link target
            title: Title used for link
            as_button: Whether link should be rendered as button
            primary_color: If rendered as button, use primary color as background.
            kwargs: keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target
        self.title = title
        self.as_button = as_button
        self.primary_color = primary_color

    def __repr__(self):
        return helpers.get_repr(
            self,
            target=self.target,
            title=self.title,
            as_button=self.as_button,
            primary_color=self.primary_color,
            _filter_empty=True,
            _filter_false=True,
        )

    def _to_markdown(self) -> str:
        match self.target:
            case mkpage.MkPage():
                path = self.target.resolved_file_path.replace(".md", ".html")
                url = (project.Project().config.site_url or "") + path
            case mknav.MkNav():
                if self.target.index_page:
                    path = self.target.index_page.resolved_file_path
                    path = path.replace(".md", ".html")
                else:
                    path = self.target.resolved_file_path
                url = (project.Project().config.site_url or "") + path
            case str() if self.target.startswith(("http:", "https:", "www.")):
                url = self.target
            case str():
                url = f"{self.target}.md"
            case _:
                raise TypeError(self.target)
        title = self.target if self.title is None else self.title
        if self.as_button:
            button_suffix = (
                "{ .md-button .md-button--primary }"
                if self.primary_color
                else "{ .md-button }"
            )
        else:
            button_suffix = ""
        return f"[{title}]({url}){button_suffix}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        url = "http://www.google.de"
        node = mknodes.MkLink(url, "This is a link.")
        page += node
        page += mknodes.MkCode(str(node), language="markdown")
        node = mknodes.MkLink(url, "This is a link.", as_button=True)
        page += node
        page += mknodes.MkCode(str(node), language="markdown")
        node = mknodes.MkLink(url, "This is a link.", as_button=True, primary_color=True)
        page += node
        page += mknodes.MkCode(str(node), language="markdown")


if __name__ == "__main__":
    link = MkLink("www.test.de")

from __future__ import annotations

import logging

from typing import Any

from mknodes import mknav
from mknodes.basenodes import mknode
from mknodes.pages import mkpage
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkImageLink(mknode.MkNode):
    """A simple image link node."""

    ICON = "material/link-box-variant-outline"

    def __init__(
        self,
        target: str | mkpage.MkPage | mknav.MkNav,
        image_url: str,
        title: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: Link target
            image_url: Image to be displayed as a link
            title: Title used for link
            kwargs: keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target
        self.title = title
        self.image_url = image_url or ""

    def __repr__(self):
        return helpers.get_repr(
            self,
            target=self.target,
            title=self.title,
            image=self.image_url,
            _filter_empty=True,
        )

    def _to_markdown(self) -> str:
        url = helpers.get_url_for(self.target)
        auto_title = url.rstrip("/").split("/")[-1]
        title = auto_title if self.title is None else self.title
        return f"[![{title}]({self.image_url})]({url})"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        node = MkImageLink(
            target="https://github.com/phil65/mknodes/actions/",
            image_url="https://github.com/phil65/mknodes/workflows/Build/badge.svg",
        )
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    link = MkImageLink(
        target="https://github.com/phil65/mknodes/actions/",
        image_url="https://github.com/phil65/mknodes/workflows/Build/badge.svg",
    )
    print(link)

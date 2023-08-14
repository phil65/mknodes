from __future__ import annotations

import logging
import pathlib

from typing import Any, Literal

from mknodes import mknav
from mknodes.basenodes import mknode
from mknodes.pages import mkpage
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkImage(mknode.MkNode):
    """Image including optional caption."""

    ICON = "material/image"
    REQUIRED_EXTENSIONS = ["attr_list", "md_in_html"]

    def __init__(
        self,
        path: str,
        *,
        link: str | mkpage.MkPage | mknav.MkNav | None = None,
        caption: str = "",
        title: str = "",
        align: Literal["left", "right"] | None = None,
        width: int | None = None,
        lazy: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            path: path of the image
            link: Optional url the image should link to
            caption: Image caption
            title: Image title
            align: Image alignment
            width: Image width in pixels
            lazy: Whether to lazy-load image
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.title = title
        self.caption = caption
        self.target = link
        self.align = align
        self.width = width
        self.lazy = lazy
        if path.startswith(("http:", "https:", "www.")):
            self.path = path
        else:
            # TODO: linkreplacer doesnt work yet with full path
            self.path = pathlib.Path(path).name  # this should not be needed.

    def __repr__(self):
        return helpers.get_repr(
            self,
            path=self.path,
            caption=self.caption,
            link=self.url,
            align=self.align,
            width=self.width,
            lazy=self.lazy,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def url(self) -> str:
        if not self.target:
            return ""
        if self.associated_project:
            config = self.associated_project.config
            base_url = config.site_url or ""
        else:
            base_url = ""
        return helpers.get_url(self.target, base_url)

    def _to_markdown(self) -> str:
        markdown_link = f"![{self.title}]({self.path})"
        if self.align:
            markdown_link += f"{{ align={self.align} }}"
        if self.width:
            markdown_link += f'{{ width="{self.width}" }}'
        if self.lazy:
            markdown_link += "{ loading=lazy }"
        if self.target:
            markdown_link = f"[{markdown_link}]({self.url})"
        if not self.caption:
            return markdown_link
        lines = [
            "<figure markdown>",
            f"  {markdown_link}",
            f"  <figcaption>{self.caption}</figcaption>",
            "</figure>",
        ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkImage(path="https://picsum.photos/200", caption="Dummy image")
        page += mknodes.MkReprRawRendered(node, header="### With caption")

        node = MkImage(path="https://picsum.photos/200", align="right")
        page += mknodes.MkReprRawRendered(node, header="### Aligned")

        node = MkImage(path="https://picsum.photos/200", width=500)
        page += mknodes.MkReprRawRendered(node, header="### Fixed width")

        node = MkImage(path="https://picsum.photos/200", link="https://www.google.com")
        page += mknodes.MkReprRawRendered(node, header="### Linked")


if __name__ == "__main__":
    img = MkImage("Some path", link="http://www.google.de", title="test")
    print(img)

from __future__ import annotations

import logging
import pathlib

from typing import Literal

from mknodes.basenodes import mknode
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
        caption: str = "",
        align: Literal["left", "right"] | None = None,
        width: int | None = None,
        lazy: bool = False,
        title: str = "Image title",
        header: str = "",
    ):
        """Constructor.

        Arguments:
            path: path of the image
            caption: Image caption
            title: Image title
            align: Image alignment
            width: Image width in pixels
            lazy: Whether to lazy-load image
            header: Section header
        """
        super().__init__(header=header)
        self.title = title
        self.caption = caption
        self.align = align
        self.width = width
        self.lazy = lazy
        if path.startswith(("http:", "https:", "www.")):
            self.path = path
        else:
            # TODO: linkreplacer doesnt work yet with full path
            self.path = pathlib.Path(path).name  # this should not be needed.

    def __repr__(self):
        kwargs = dict(
            path=self.path,
            caption=self.caption,
            align=self.align,
            width=self.width,
        )
        if self.lazy:
            kwargs["lazy"] = True
        return helpers.get_repr(self, _filter_empty=True, **kwargs)

    def _to_markdown(self) -> str:
        markdown_link = f"![{self.title}]({self.path})"
        if self.align:
            markdown_link += f"{{ align={self.align} }}"
        if self.width:
            markdown_link += f'{{ width="{self.width}" }}'
        if self.lazy:
            markdown_link += "{ loading=lazy }"
        if not self.caption:
            return markdown_link
        lines = ["<figure markdown>", f"  {markdown_link}"]
        lines.append(f"  <figcaption>{self.caption}</figcaption>")
        lines.append("</figure>")
        return "\n".join(lines) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "A simple MkNode to display an image. Target can be local or remote."

        node = MkImage(path="https://picsum.photos/200", caption="Dummy image")
        page += mknodes.MkReprRawRendered(node)

        node = MkImage(path="https://picsum.photos/200", align="right")
        page += mknodes.MkReprRawRendered(node)

        node = MkImage(path="https://picsum.photos/200", width=500)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkImage("Some path")

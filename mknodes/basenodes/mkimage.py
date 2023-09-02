from __future__ import annotations

import logging
import pathlib

from typing import Any, Literal

from mknodes import mknav
from mknodes.basenodes import mknode
from mknodes.pages import mkpage
from mknodes.utils import helpers, linkprovider, reprhelpers


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
        path_dark_mode: str | None = None,
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
            path_dark_mode: Optional alternative image for dark mode
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.title = title
        self.caption = caption
        self.target = link
        self.align = align
        self.width = width
        self.lazy = lazy
        self._path_dark_mode = path_dark_mode
        self._path = path

    @property
    def path(self):
        if helpers.is_url(self._path):
            return self._path
        # TODO: linkreplacer doesnt work yet with full path
        return pathlib.Path(self._path).name  # this should not be needed.

    @property
    def path_dark_mode(self):
        match self._path_dark_mode:
            case str() if helpers.is_url(self._path_dark_mode):
                return self._path_dark_mode
            case str():
                return pathlib.Path(self._path_dark_mode).name
            case _:
                return None

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            path=self.path,
            caption=self.caption,
            link=self.url,
            align=self.align,
            width=self.width,
            lazy=self.lazy,
            path_dark_mode=self.path_dark_mode,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def url(self) -> str:
        if not self.target:
            return ""
        if self.associated_project:
            return self.associated_project.linkprovider.get_url(self.target)
        return linkprovider.LinkProvider().get_url(self.target)

    def _to_markdown(self) -> str:
        if not self.path_dark_mode:
            markdown_link = self._build(self.path)
        else:
            link_2 = self._build(self.path, "light")
            link_1 = self._build(self.path_dark_mode, "dark")
            markdown_link = f"{link_1} {link_2}"
        if not self.caption:
            return markdown_link
        lines = [
            "<figure markdown>",
            f"  {markdown_link}",
            f"  <figcaption>{self.caption}</figcaption>",
            "</figure>",
        ]
        return "\n".join(lines) + "\n"

    def _build(self, path, mode: Literal["light", "dark"] | None = None) -> str:
        if mode:
            path += f"#only-{mode}"
        markdown_link = f"![{self.title}]({path})"
        if self.align:
            markdown_link += f"{{ align={self.align} }}"
        if self.width:
            markdown_link += f'{{ width="{self.width}" }}'
        if self.lazy:
            markdown_link += "{ loading=lazy }"
        if self.target:
            markdown_link = f"[{markdown_link}]({self.url})"
        return markdown_link

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

        node = MkImage(
            path="https://picsum.photos/200",
            link="https://www.google.com",
            path_dark_mode="https://picsum.photos/300",
        )
        page += mknodes.MkReprRawRendered(node, header="### Separate dark mode")


if __name__ == "__main__":
    img = MkImage("Some path", link="http://www.google.de", title="test")
    print(img)

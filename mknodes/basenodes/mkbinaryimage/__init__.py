from __future__ import annotations

import os
import upath

from typing import Any, Literal, Self

from mknodes.basenodes import mkimage
from mknodes.info import linkprovider
from mknodes.utils import helpers, icons, log


logger = log.get_logger(__name__)


class MkBinaryImage(mkimage.MkImage):
    """Image carrying the data by itself.

    This node basically is a regular image link, but carries the image data by itself.
    The data will get written to the "virtual" folder at the end of the process.
    It can hold either str or bytes as data.
    """

    ICON = "material/file-image"

    def __init__(
        self,
        data: bytes | str,
        path: str,
        *,
        target: linkprovider.LinkableType | None = None,
        caption: str = "",
        title: str = "",
        align: Literal["left", "right"] | None = None,
        width: int | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            data: Image data
            path: path for the image (including extension)
            target: Optional URL or node the image should link to
            caption: Image caption
            title: Image title
            align: Image alignment
            width: Image width in pixels
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            path=path,
            target=target,
            caption=caption,
            title=title,
            align=align,
            width=width,
            **kwargs,
        )
        self.data = data

    @property
    def files(self) -> dict[str, str | bytes]:
        path = "/".join(self.resolved_parts) + "/" + self.path
        return {path: self.data} | self._files

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += "A BinaryImage carries the image data by itself."
        page += "A file containing the data will become part of the file tree later on."
        data = """<svg width="90pt" height="90pt" version="1.1"
        viewBox="0 0 15.875 10.583" xmlns="http://www.w3.org/2000/svg">
         <g fill="none" stroke="#F00" stroke-width=".3">
          <path d="m6.1295 3.6601 3.2632 3.2632z"/>
          <path d="m9.3927 3.6601-3.2632 3.2632z"/>
         </g>
        </svg>
        """
        node = MkBinaryImage(data, path="some_image.svg", caption="A simple cross")
        page += mk.MkHeader("From data", level=3)
        page += mk.MkReprRawRendered(node)
        node = MkBinaryImage.for_icon("file-image", width=200)
        page += mk.MkHeader("From icon", level=3)
        page += mk.MkReprRawRendered(node)

    @classmethod
    def for_icon(cls, icon: str, **kwargs: Any) -> Self:
        """Return a MkBinaryImage with data for given icon.

        Arguments:
            icon: Icon to get a MkBinaryImage for (example: material/file-image)
            kwargs: Keyword arguments passed to constructor
        """
        content = icons.get_icon_svg(icon)
        path = f"{helpers.slugify(icon)}.svg"
        return cls(data=content, path=path, **kwargs)

    @classmethod
    def for_file(
        cls,
        path: str | os.PathLike,
        storage_options: dict | None = None,
        **kwargs: Any,
    ) -> Self:
        """Return a MkBinaryImage with data for given icon.

        Arguments:
            path: Path to an image (also takes fsspec protocol URLs)
            storage_options: Options for fsspec backend
            kwargs: Keyword arguments passed to constructor
        """
        opts = storage_options or {}
        file = upath.UPath(path, **opts)
        return cls(data=file.read_bytes(), path=file.name, **kwargs)


if __name__ == "__main__":
    node = MkBinaryImage.for_file("assets/cli.gif")
    print(node.data)

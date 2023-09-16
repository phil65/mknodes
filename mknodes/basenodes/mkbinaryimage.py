from __future__ import annotations

import os
import pathlib

from typing import Any, Self

from mknodes.basenodes import mkimage
from mknodes.utils import helpers, log, pathhelpers


logger = log.get_logger(__name__)


class MkBinaryImage(mkimage.MkImage):
    """Image carrying the data by itself.

    This node basically is a regular image link, but carries the image data by itself.
    The data will get written to the "virtual" folder at the end of the process.
    It can hold either str or bytes as data.
    """

    ICON = "material/file-image"

    def __init__(self, data: bytes | str, path: str, **kwargs: Any):
        """Constructor.

        Arguments:
            data: Image data
            path: path for the image (including extension)
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(path=path, **kwargs)
        self.data = data

    @property
    def files(self):
        path = "/".join(self.resolved_parts) + "/" + self.path
        return {path: self.data} | self._files

    @staticmethod
    def create_example_page(page):
        import mknodes

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
        page += mknodes.MkHeader("From data", level=3)
        page += mknodes.MkReprRawRendered(node)
        node = MkBinaryImage.for_icon("file-image", width=200)
        page += mknodes.MkHeader("From icon", level=3)
        page += mknodes.MkReprRawRendered(node)

    @classmethod
    def for_icon(cls, icon: str, **kwargs: Any) -> Self:
        """Return a MkBinaryImage with data for given icon.

        Arguments:
            icon: Icon to get a MkBinaryImage for (example: material/file-image)
            kwargs: Keyword arguments passed to constructor
        """
        if "/" not in icon:
            icon = f"material/{icon}"
        icon_path = pathhelpers.get_material_icon_path(icon)
        content = icon_path.read_text()
        path = f"{helpers.slugify(icon)}.svg"
        return cls(data=content, path=path, **kwargs)

    @classmethod
    def for_file(cls, path: str | os.PathLike, **kwargs: Any) -> Self:
        """Return a MkBinaryImage with data for given icon.

        Arguments:
            path: Icon to get a MkBinaryImage for (example: material/file-image)
            kwargs: Keyword arguments passed to constructor
        """
        path = pathlib.Path(path)
        content = path.read_bytes()
        path = path.name
        return cls(data=content, path=path, **kwargs)


if __name__ == "__main__":
    node = MkBinaryImage.for_file("assets/cli.gif")
    print(node.data)

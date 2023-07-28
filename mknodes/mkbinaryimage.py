from __future__ import annotations

import logging

from mknodes import mkimage


logger = logging.getLogger(__name__)


class MkBinaryImage(mkimage.MkImage):
    """Image carrying the data by itself.

    This node basically is a regular image link, but carries the image data by itself.
    The data will get written to the "virtual" folder at the end of the process.
    It can hold either str or bytes as data.
    """

    def __init__(
        self,
        data: bytes | str,
        path: str,
        *,
        caption: str = "",
        title: str = "Image title",
        header: str = "",
    ):
        super().__init__(path=path, header=header, caption=caption, title=title)
        self.data = data

    def virtual_files(self):
        return {self.path: self.data}

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "A BinaryImage carries the image data by itself."
        page += "A file containing the data will become part of the file tree later on."
        data = """<svg width="45pt" height="30pt" version="1.1"
        viewBox="0 0 15.875 10.583" xmlns="http://www.w3.org/2000/svg">
         <g fill="none" stroke="#000" stroke-width=".17639">
          <path d="m6.1295 3.6601 3.2632 3.2632z"/>
          <path d="m9.3927 3.6601-3.2632 3.2632z"/>
         </g>
        </svg>
        """
        node = MkBinaryImage(data, path="some_image.svg", caption="A simple cross")
        page += node
        page += mknodes.MkCode(str(node), language="markdown", header="Markdown")

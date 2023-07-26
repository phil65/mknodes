from __future__ import annotations

import logging

from mknodes import mkimage


logger = logging.getLogger(__name__)


class MkBinaryImage(mkimage.MkImage):
    """Binary data of an image which will become a file when the tree is written."""

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

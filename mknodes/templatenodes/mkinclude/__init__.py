from __future__ import annotations

import os

from typing import Any

from mknodes.basenodes import mktext
from mknodes.pages import mkpage
from mknodes.utils import log, pathhelpers


EXAMPLE_URL = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"


logger = log.get_logger(__name__)


class MkInclude(mktext.MkText):
    """Node to include the text of other Markdown files / MkNodes.

    This node only keeps a reference to given target and resolves it when needed.
    Target can either be an URL or any other fsspec protocol path to a markdown file,
    a file system path to a markdown file, or another MkNode.
    """

    ICON = "octicons/file-symlink-file-24"

    def __init__(self, target: str | os.PathLike | mktext.MkText, **kwargs: Any):
        """Constructor.

        Arguments:
            target: target to include
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target

    @property
    def text(self) -> str:
        match self.target:
            case os.PathLike() | str():
                return pathhelpers.load_file_cached(str(self.target))
            case mktext.MkText():
                return str(self.target)
            case _:
                raise TypeError(self.target)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkInclude(EXAMPLE_URL)
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    page = mkpage.MkPage(content="test")
    include = MkInclude(target=EXAMPLE_URL)
    print(include)

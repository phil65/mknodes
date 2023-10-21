from __future__ import annotations

import os

from typing import Any

from mknodes.basenodes import mknode
from mknodes.pages import mkpage
from mknodes.utils import log, pathhelpers, reprhelpers


EXAMPLE_URL = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"


logger = log.get_logger(__name__)


class MkInclude(mknode.MkNode):
    """Node to include the text of other Markdown files / MkNodes.

    This node only keeps a reference to given target and resolves it when needed.
    Target can either be an URL or any other fsspec protocol path to a markdown file,
    a file system path to a markdown file, or another MkNode.
    """

    ICON = "octicons/file-symlink-file-24"

    def __init__(
        self,
        target: str | os.PathLike | mknode.MkNode,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            target: target to include
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target

    def __repr__(self):
        return reprhelpers.get_repr(self, target=self.target)

    def _to_markdown(self) -> str:  # type: ignore[return]
        match self.target:
            case os.PathLike() | str():
                return pathhelpers.load_file_cached(str(self.target))
            case mknode.MkNode():
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

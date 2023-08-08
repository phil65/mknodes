from __future__ import annotations

import logging
import os

from typing import Any, Literal, get_args

from mknodes import treelib
from mknodes.basenodes import mkcode, mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


DirectoryTreeStyleStr = Literal[
    "ansi",
    "ascii",
    "const",
    "const_bold",
    "rounded",
    "double",
    "spaces",
]


class MkDirectoryTree(mkcode.MkCode):
    """Node to display directory content as a tree.

    Based on "seedir" package

    """

    ICON = "material/file-tree-outline"

    def __init__(
        self,
        directory: str | os.PathLike | treelib.Node,
        *,
        style: DirectoryTreeStyleStr | tuple[str, str, str] | None = None,
        maximum_depth: int | None = None,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            directory: Folder path to prettyprint content from
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header, **kwargs)
        self.directory = directory
        self.style = style
        self.maximum_depth = maximum_depth

    @property
    def text(self):
        match self.directory:
            case str() | os.PathLike():
                node = treelib.FileTreeNode.from_folder(self.directory)
            case mknode.MkNode():
                node = self.directory
            case _:
                raise TypeError(self.directory)
        return treelib.get_tree_repr(
            node,
            style=self.style,
            max_depth=self.maximum_depth,
        )

    @text.setter
    def text(self, text):
        self.obj = text

    def __repr__(self):
        return helpers.get_repr(
            self,
            path=str(self.directory),
            style=self.style,
            maximum_depth=self.maximum_depth,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        for style in get_args(DirectoryTreeStyleStr):
            node = MkDirectoryTree("mknodes/manual", style=style)
            page += mknodes.MkReprRawRendered(node, header=f"### Style '{style}'")


if __name__ == "__main__":
    node = MkDirectoryTree(".", header="test", style="ascii")
    print(node.to_markdown())
    print(MkDirectoryTree(node, style="ascii"))

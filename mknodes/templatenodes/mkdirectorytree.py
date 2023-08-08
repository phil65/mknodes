from __future__ import annotations

from collections.abc import Callable
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
    """Node to display directory content as a tree."""

    ICON = "material/file-tree-outline"

    def __init__(
        self,
        directory: str | os.PathLike | treelib.Node,
        *,
        style: DirectoryTreeStyleStr | tuple[str, str, str] | None = None,
        maximum_depth: int | None = None,
        predicate: Callable | None = None,
        exclude_folders: list[str] | str | None = None,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            directory: Folder path to prettyprint content from
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            predicate: Predicate to filter results
            exclude_folders: Folders to exclude from listing
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header, **kwargs)
        self.tree = directory
        self.style = style
        self.predicate = predicate
        self.maximum_depth = maximum_depth
        self.exclude_folders = (
            [exclude_folders] if isinstance(exclude_folders, str) else exclude_folders
        )

    @property
    def text(self):
        match self.tree:
            case str() | os.PathLike():
                node = treelib.FileTreeNode.from_folder(
                    self.tree,
                    predicate=self.predicate,
                    exclude_folders=self.exclude_folders,
                )
                return treelib.get_tree_repr(
                    node,
                    style=self.style or "rounded",
                    max_depth=self.maximum_depth or 0,
                )
            case mknode.MkNode():
                # lines = [
                #     f"{level * '    '} {node!r}" for level, node in
                # self.tree.iter_nodes()
                # ]
                # return "\n".join(lines)
                return treelib.get_tree_repr(
                    self.tree,
                    style=self.style or "rounded",
                    max_depth=self.maximum_depth or 0,
                )

    @text.setter
    def text(self, text):
        self.obj = text

    def __repr__(self):
        return helpers.get_repr(
            self,
            path=str(self.tree),
            style=self.style or "rounded",
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

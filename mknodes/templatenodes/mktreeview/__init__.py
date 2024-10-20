from __future__ import annotations

import os
import upath

from typing import Any, TYPE_CHECKING

from mknodes import treelib
from mknodes.basenodes import mkcode, mknode
from mknodes.utils import log

if TYPE_CHECKING:
    from mknodes.data import treestyles
    from collections.abc import Callable


logger = log.get_logger(__name__)


class MkTreeView(mkcode.MkCode):
    """Node to display tree structures.

    Currently supports directories and Node subclasses (including `MkNodes`).
    """

    ICON = "material/file-tree-outline"
    STATUS = "new"

    def __init__(
        self,
        tree: str | os.PathLike[str] | treelib.Node,
        *,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] = "rounded",
        maximum_depth: int | None = None,
        predicate: Callable | None = None,
        exclude_folders: list[str] | str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            tree: Tree to display. Can be a path to a folder or a Node.
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            predicate: Predicate to filter results
            exclude_folders: Folders to exclude from listing
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(language="", **kwargs)
        self._tree = tree
        self.style = style
        self.predicate = predicate
        self.maximum_depth = maximum_depth
        self.exclude_folders = (
            [exclude_folders] if isinstance(exclude_folders, str) else exclude_folders
        )

    @property
    def tree(self) -> treelib.Node:
        match self._tree:
            case str() | os.PathLike():
                return treelib.FileTreeNode.from_folder(
                    upath.UPath(self._tree),
                    predicate=self.predicate,
                    exclude_folders=self.exclude_folders,
                    maximum_depth=self.maximum_depth,
                )
            case mknode.MkNode():
                return self._tree
            case _:
                raise TypeError(self._tree)

    @property
    def text(self):
        return self.tree.get_tree_repr(style=self.style, max_depth=self.maximum_depth)


if __name__ == "__main__":
    node = MkTreeView(
        upath.UPath("github://mknodes", org="mkdocstrings", repo="mkdocstrings"),
        style="ascii",
        maximum_depth=2,
    )
    print(node.to_markdown())

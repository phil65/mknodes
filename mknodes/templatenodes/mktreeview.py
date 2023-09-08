from __future__ import annotations

from collections.abc import Callable
import os
import pathlib

from typing import Any, get_args

from mknodes import treelib
from mknodes.basenodes import mkcode, mknode
from mknodes.data import treestyles
from mknodes.utils import fsspecpath, log, reprhelpers


logger = log.get_logger(__name__)


class MkTreeView(mkcode.MkCode):
    """Node to display tree structures.

    Currently supports directories and Node subclasses (including `MkNodes`).
    """

    ICON = "material/file-tree-outline"
    STATUS = "new"

    def __init__(
        self,
        tree: str | os.PathLike | treelib.Node,
        *,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] | None = None,
        maximum_depth: int | None = None,
        predicate: Callable | None = None,
        exclude_folders: list[str] | str | None = None,
        header: str = "",
        storage_options: dict | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            tree: Tree to display. Can be a path to a folder or a Node.
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            predicate: Predicate to filter results
            exclude_folders: Folders to exclude from listing
            header: Section header
            storage_options: Used when tree is a fsspec path
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header, language="", **kwargs)
        self.tree = tree
        self._style = style
        self.predicate = predicate
        self.maximum_depth = maximum_depth
        self.storage_options = storage_options or {}
        self.exclude_folders = (
            [exclude_folders] if isinstance(exclude_folders, str) else exclude_folders
        )

    @property
    def text(self):
        match self.tree:
            case str() if "://" in self.tree:
                protocol, path = self.tree.split("://", 1)
                node = treelib.FileTreeNode.from_folder(
                    fsspecpath.FsSpecPath(path, protocol, **self.storage_options),
                    predicate=self.predicate,
                    exclude_folders=self.exclude_folders,
                    maximum_depth=self.maximum_depth,
                )
            case str() | os.PathLike():
                node = treelib.FileTreeNode.from_folder(
                    pathlib.Path(self.tree),
                    predicate=self.predicate,
                    exclude_folders=self.exclude_folders,
                    maximum_depth=self.maximum_depth,
                )
            case mknode.MkNode():
                node = self.tree
            case None:
                return ""
            case _:
                raise TypeError(self.tree)
        return node.get_tree_repr(style=self.style, max_depth=self.maximum_depth)

    @text.setter
    def text(self, text):
        self.obj = text

    @property
    def style(self) -> treestyles.TreeStyleStr | tuple[str, str, str, str]:
        return self._style or "rounded"

    @style.setter
    def style(self, value: treestyles.TreeStyleStr | tuple[str, str, str, str] | None):
        self._style = value

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            path=str(self.tree),
            style=self._style,
            maximum_depth=self.maximum_depth,
            exclude_folders=self.exclude_folders,
            storage_options=self.storage_options,
            _filter_empty=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        # Different styles
        for style in get_args(treestyles.TreeStyleStr):
            node = MkTreeView("mknodes/manual", style=style)
            page += mknodes.MkReprRawRendered(node, header=f"### Style '{style}'")

        # Showing a remote tree structure (using fsspec package)
        # opts = dict(org="mkdocstrings", repo="mkdocstrings")
        # node = MkTreeView("github://", storage_options=opts, maximum_depth=2)
        # page += mknodes.MkReprRawRendered(node, header="### From remote (FsSpec)")


if __name__ == "__main__":
    opts = dict(org="mkdocstrings", repo="mkdocstrings")
    node = MkTreeView(
        "github://",
        storage_options=opts,
        header="test",
        style="ascii",
        maximum_depth=2,
    )
    print(node.to_markdown())

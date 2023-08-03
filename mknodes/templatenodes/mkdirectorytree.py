from __future__ import annotations

import logging
import os
import pathlib

from typing import Any, Literal

import seedir

from mknodes.basenodes import mkcode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkDirectoryTree(mkcode.MkCode):
    """Node to display directory content as a tree.

    Based on "seedir" package

    """

    ICON = "material/file-tree-outline"

    def __init__(
        self,
        directory: str | os.PathLike,
        *,
        style: Literal["lines", "dash", "arrow", "spaces", "plus", "emoji"] | None = None,
        indent: int = 4,
        depth_limit: int | None = None,
        item_limit: int | None = None,
        beyond: Literal["ellipsis", "content"] = "ellipsis",
        first: Literal["files", "folders"] | None = None,
        sort: bool = False,
        exclude_folders: list[str] | str | None = None,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            directory: Folder path to prettyprint content from
            style: Print style
            indent: Specifies the amount of indentation added for each nesting level
            depth_limit: Maximum nesting depth to print
            item_limit: Maximum amount of items to print
            beyond: String to indicate directory contents beyond the limits.
            first: What to print first
            sort: Whether to sort the output
            exclude_folders: Folders to exclude from listing
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header, **kwargs)
        self.directory = pathlib.Path(directory)
        self.style = style or "lines"
        self.print_indent = indent
        self.depth_limit = depth_limit
        self.item_limit = item_limit
        self.beyond = beyond
        self.first = first
        self.sort = sort
        self.exclude_folders = exclude_folders

    @property
    def text(self):
        return seedir.seedir(
            self.directory,
            style=self.style,
            printout=False,
            indent=self.print_indent,
            depthlimit=self.depth_limit,
            itemlimit=self.item_limit,
            beyond=self.beyond,
            first=self.first,
            sort=self.sort,
            exclude_folders=self.exclude_folders,
        )

    @text.setter
    def text(self, text):
        self.obj = text

    def __repr__(self):
        return helpers.get_repr(
            self,
            path=str(self.directory),
            style=self.style,
            printout=False,
            indent=self.print_indent,
            depth_limit=self.depth_limit,
            item_limit=self.item_limit,
            beyond=self.beyond,
            first=self.first,
            sort=self.sort,
            exclude_folders=self.exclude_folders,
            _filter_empty=True,
            _filter_false=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        node = MkDirectoryTree("mknodes")
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    node = MkDirectoryTree(".", header="test", style="dash")
    print(node.to_markdown())

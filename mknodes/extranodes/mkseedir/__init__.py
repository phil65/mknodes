from __future__ import annotations

import upath

from typing import Any, Literal, TYPE_CHECKING

from mknodes.basenodes import mkcode
from mknodes.utils import helpers, log, resources

if TYPE_CHECKING:
    import os


logger = log.get_logger(__name__)


DirectoryTreeStyleStr = Literal["lines", "dash", "arrow", "spaces", "plus"]


@helpers.list_to_tuple
def get_folder_tree(
    directory: str | os.PathLike[str],
    *,
    style: DirectoryTreeStyleStr | None = None,
    indent: int = 4,
    depth_limit: int | None = None,
    item_limit: int | None = None,
    beyond: Literal["ellipsis", "content"] = "ellipsis",
    first: Literal["files", "folders"] | None = None,
    sort: bool = False,
    exclude_folders: list[str] | str | None = None,
) -> str:
    import seedir

    return seedir.seedir(
        directory,
        style=style or "lines",
        printout=False,
        indent=indent,
        depthlimit=depth_limit,
        itemlimit=item_limit,
        beyond=beyond,
        first=first,
        sort=sort,
        exclude_folders=exclude_folders,
    )


class MkSeeDir(mkcode.MkCode):
    """Node to display directory content as a tree.

    Based on "seedir" package

    """

    ICON = "material/file-tree-outline"
    REQUIRED_PACKAGES = [resources.Package("seedir")]

    def __init__(
        self,
        directory: str | os.PathLike[str],
        *,
        style: DirectoryTreeStyleStr | None = None,
        print_indent: int = 4,
        depth_limit: int | None = None,
        item_limit: int | None = None,
        beyond: Literal["ellipsis", "content"] = "ellipsis",
        first: Literal["files", "folders"] | None = None,
        sort: bool = False,
        exclude_folders: list[str] | str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            directory: Folder path to prettyprint content from
            style: Print style
            print_indent: Amount of indentation added for each nesting level
            depth_limit: Maximum nesting depth to print
            item_limit: Maximum amount of items to print
            beyond: String to indicate directory contents beyond the limits.
            first: What to print first
            sort: Whether to sort the output
            exclude_folders: Folders to exclude from listing
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.directory = upath.UPath(directory)
        self.style = style or "lines"
        self.print_indent = print_indent
        self.depth_limit = depth_limit
        self.item_limit = item_limit
        self.beyond = beyond
        self.first = first
        self.sort = sort
        self.exclude_folders = exclude_folders

    @property
    def text(self):
        return get_folder_tree(
            self.directory,
            style=self.style,
            indent=self.print_indent,
            depth_limit=self.depth_limit,
            item_limit=self.item_limit,
            beyond=self.beyond,
            first=self.first,
            sort=self.sort,
            exclude_folders=self.exclude_folders,
        )

    @text.setter
    def text(self, text):
        self.obj = text


if __name__ == "__main__":
    node = MkSeeDir(".", style="dash")
    print(node.to_markdown())

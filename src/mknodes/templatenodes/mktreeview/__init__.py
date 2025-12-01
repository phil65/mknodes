from __future__ import annotations

import os
import upath

from typing import Any, TYPE_CHECKING
from upathtools import filetree
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
        tree: str | os.PathLike[str] | upath.UPath | mknode.MkNode,
        *,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] = "rounded",
        maximum_depth: int | None = None,
        predicate: Callable[..., bool] | None = None,
        exclude_folders: list[str] | str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            tree: Tree to display. Can be a path to a folder or a Node.
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            predicate: Predicate to filter results
            exclude_folders: Folders to exclude from listing
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(language="", **kwargs)
        self.tree = tree
        self.style: treestyles.TreeStyleStr | tuple[str, str, str, str] = style
        self.predicate = predicate
        self.maximum_depth = maximum_depth
        self.exclude_folders = (
            [exclude_folders] if isinstance(exclude_folders, str) else exclude_folders
        )

    async def get_text(self) -> str:
        match self.tree:
            case str() | os.PathLike() | upath.UPath():
                return filetree.get_directory_tree(
                    self.tree, max_depth=self.maximum_depth, show_size=True
                )
            case mknode.MkNode() as tree:
                return tree.get_tree_repr(style=self.style, max_depth=self.maximum_depth)
            case _:  # pyright: ignore[reportUnnecessaryComparison]
                raise TypeError(self.tree)


if __name__ == "__main__":
    import asyncio

    async def main() -> None:
        """Example."""
        p = upath.UPath("github://phil65:jinjarope@main/tests/testresources")
        node = MkTreeView(p, style="ascii", maximum_depth=2)
        print(await node.to_markdown())

    asyncio.run(main())

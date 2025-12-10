from __future__ import annotations

import os
import re
import upath

from typing import Any, TYPE_CHECKING
from upathtools import filetree
from mknodes.basenodes import mkcode, mknode
from mknodes.utils import log

if TYPE_CHECKING:
    from upath.types import JoinablePathLike
    from mknodes.data import treestyles
    from collections.abc import Callable
    from upathtools.filetree import SortCriteria


logger = log.get_logger(__name__)


class MkTreeView(mkcode.MkCode):
    """Node to display tree structures.

    Currently supports directories and Node subclasses (including `MkNodes`).
    """

    ICON = "material/file-tree-outline"
    STATUS = "new"

    def __init__(
        self,
        tree: JoinablePathLike | mknode.MkNode,
        *,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] = "rounded",
        maximum_depth: int | None = None,
        predicate: Callable[..., bool] | None = None,
        exclude_patterns: list[str] | str | None = None,
        include_patterns: list[str] | str | None = None,
        allowed_extensions: set[str] | list[str] | None = None,
        show_hidden: bool = False,
        show_size: bool = True,
        show_date: bool = False,
        show_permissions: bool = False,
        show_icons: bool = True,
        hide_empty: bool = False,
        sort_by: SortCriteria = "name",
        reverse_sort: bool = False,
        date_format: str = "%Y-%m-%d %H:%M:%S",
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            tree: Tree to display. Can be a path to a folder or a Node.
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            predicate: Predicate to filter results
            exclude_patterns: Glob patterns to exclude (e.g., "*.pyc", "__pycache__")
            include_patterns: Glob patterns to include (only matching files shown)
            allowed_extensions: Set/list of allowed file extensions (e.g., {".py", ".md"})
            show_hidden: Whether to show hidden files/directories (starting with .)
            show_size: Whether to show file sizes
            show_date: Whether to show modification dates
            show_permissions: Whether to show file permissions
            show_icons: Whether to show icons for files/directories
            hide_empty: Whether to hide empty directories after filtering
            sort_by: Sort criteria - "name", "size", "date", or "type"
            reverse_sort: Whether to reverse the sort order
            date_format: Format string for dates (when show_date=True)
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(language="", **kwargs)
        self.tree = tree
        self.style: treestyles.TreeStyleStr | tuple[str, str, str, str] = style
        self.predicate = predicate
        self.maximum_depth = maximum_depth
        self.exclude_patterns = (
            [exclude_patterns] if isinstance(exclude_patterns, str) else exclude_patterns
        )
        self.include_patterns = (
            [include_patterns] if isinstance(include_patterns, str) else include_patterns
        )
        self.allowed_extensions = (
            set(allowed_extensions) if isinstance(allowed_extensions, list) else allowed_extensions
        )
        self.show_hidden = show_hidden
        self.show_size = show_size
        self.show_date = show_date
        self.show_permissions = show_permissions
        self.show_icons = show_icons
        self.hide_empty = hide_empty
        self.sort_by: SortCriteria = sort_by
        self.reverse_sort = reverse_sort
        self.date_format = date_format

    async def get_text(self) -> str:
        match self.tree:
            case str() | os.PathLike() | upath.UPath():
                # Convert exclude_patterns list to regex pattern
                exclude_pattern = None
                if self.exclude_patterns:
                    # Convert glob patterns to regex
                    patterns = []
                    for pattern in self.exclude_patterns:
                        # Convert glob wildcards to regex
                        # ** for recursive directories, * for any characters
                        regex_pattern = (
                            pattern.replace(".", r"\.")
                            .replace("**", "DOUBLESTAR")
                            .replace("*", "[^/]*")
                            .replace("DOUBLESTAR", ".*")
                        )
                        patterns.append(regex_pattern)
                    # Combine all patterns with OR
                    combined = "|".join(f"({p})" for p in patterns)
                    exclude_pattern = re.compile(combined)

                # Convert include_patterns list to regex pattern
                include_pattern = None
                if self.include_patterns:
                    patterns = []
                    for pattern in self.include_patterns:
                        regex_pattern = (
                            pattern.replace(".", r"\.")
                            .replace("**", "DOUBLESTAR")
                            .replace("*", "[^/]*")
                            .replace("DOUBLESTAR", ".*")
                        )
                        patterns.append(regex_pattern)
                    combined = "|".join(f"({p})" for p in patterns)
                    include_pattern = re.compile(combined)

                return filetree.get_directory_tree(
                    self.tree,
                    max_depth=self.maximum_depth,
                    show_hidden=self.show_hidden,
                    show_size=self.show_size,
                    show_date=self.show_date,
                    show_permissions=self.show_permissions,
                    show_icons=self.show_icons,
                    exclude_pattern=exclude_pattern,
                    include_pattern=include_pattern,
                    allowed_extensions=self.allowed_extensions,
                    hide_empty=self.hide_empty,
                    sort_criteria=self.sort_by,
                    reverse_sort=self.reverse_sort,
                    date_format=self.date_format,
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

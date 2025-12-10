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
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            tree: Tree to display. Can be a path to a folder or a Node.
            style: Print style. If tuple, parts are used for stems
            maximum_depth: Maximum nesting depth to print
            predicate: Predicate to filter results
            exclude_patterns: Glob patterns to exclude (e.g., "*.pyc", "__pycache__")
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

                return filetree.get_directory_tree(
                    self.tree,
                    max_depth=self.maximum_depth,
                    show_size=True,
                    show_hidden=True,
                    exclude_pattern=exclude_pattern,
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

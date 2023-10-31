from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkHeader(mknode.MkNode):
    """Super simple header node."""

    ICON = "material/format-header-pound"
    STATUS = "new"

    def __init__(
        self,
        text: str | mknode.MkNode | None = "",
        *,
        level: int = 2,
        exclude_from_search: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Header text
            level: Header level
            exclude_from_search: Whether section should be included in search.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.text = str(text or "")
        self.level = level
        self.exclude_from_search = exclude_from_search

    def _to_markdown(self) -> str:
        level_str = "#" * self.level
        suffix = " { data-search-exclude }" if self.exclude_from_search else ""
        return f"{level_str} {self.text}{suffix}"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        for i in range(1, 7):
            node = MkHeader(f"Level {i}", level=i)
            page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    header = MkHeader("Header!", level=1)
    print(header)

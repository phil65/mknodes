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
    ) -> None:
        """Constructor.

        Args:
            text: Header text
            level: Header level
            exclude_from_search: Whether section should be included in search.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._text = str(text or "")
        self.level = level
        self.exclude_from_search = exclude_from_search

    async def to_md_unprocessed(self) -> str:
        level_str = "#" * self.level
        suffix = " { data-search-exclude }" if self.exclude_from_search else ""
        return f"{level_str} {self._text}{suffix}"

    async def get_text(self) -> str:
        return self._text


if __name__ == "__main__":
    header = MkHeader("Header!", level=1)
    print(header)

from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkHeader(mknode.MkNode):
    """Super simple header node."""

    ICON = "material/format-header-pound"
    STATUS = "new"

    def __init__(
        self,
        text: str | mknode.MkNode | None = "",
        level: int = 2,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Header text
            level: Header level
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.text = str(text or "")
        self.level = level

    def __repr__(self):
        return helpers.get_repr(self, text=self.text, level=self.level)

    def _to_markdown(self) -> str:
        level_str = "#" * self.level
        return f"{level_str} {self.text}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        for i in range(1, 7):
            node = MkHeader(f"Level {i}", level=i)
            page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    header = MkHeader("Header!", level=1)
    print(header)

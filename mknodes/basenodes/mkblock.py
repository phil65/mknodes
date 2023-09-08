from __future__ import annotations

import textwrap

from typing import Any

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkBlock(mkcontainer.MkContainer):
    """PyMdown-based block."""

    ICON = "material/cube"

    def __init__(
        self,
        name: str,
        content: list | str | mknode.MkNode = "",
        *,
        argument: str = "",
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            name: Block name
            content: Block content
            argument: Block argument
            attributes: Block attributes
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.name = name
        self.attributes = attributes or {}
        self.argument = argument

    @property
    def fence_boundary(self) -> str:
        """Return the fence boundary ("///") based on nesting depth."""
        block_level = sum(isinstance(i, MkBlock) for i in self.ancestors)
        return "/" * (block_level + 3)

    @property
    def content_block(self) -> str:
        """Returns the block content. Can be reimplemented by subclasses."""
        return textwrap.indent(super()._to_markdown(), self.indent).rstrip("\n") + "\n"

    @property
    def attributes_block(self) -> str:
        """The text block for attributes.

        For subclasses, implement a property for self.attributes.
        """
        if not self.attributes:
            return ""
        lines = [f"    {k}: {v}" for k, v in self.attributes.items() if v is not None]
        return "\n".join(lines) + "\n"

    def _to_markdown(self) -> str:
        boundary = self.fence_boundary
        base = f"{boundary} {self.name}"
        if self.argument:
            base += f" | {self.argument}"
        return f"{base}\n{self.attributes_block}\n{self.content_block}{boundary}\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "An MkBlock is a base class for pymdownx-style blocks."
        block = MkBlock("html", content="Some text", argument="div")
        page += mknodes.MkCode(str(block), header="### Markdown")
        # We can also nest blocks, they will adjust their delimiters automatically.
        page += mknodes.MkHtmlBlock(block, header="### Nested")


if __name__ == "__main__":
    inner_1 = MkBlock("inner_1", content="inner_1 content")
    inner_2 = MkBlock("inner_2", content="inner_2 content")
    outer = MkBlock("outer", content=[inner_1, inner_2])
    print(outer)

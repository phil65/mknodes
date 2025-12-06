from __future__ import annotations

import textwrap

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, resources


if TYPE_CHECKING:
    import mknodes as mk

logger = log.get_logger(__name__)


class MkBlock(mkcontainer.MkContainer):
    """PyMdown-based block."""

    ICON = "material/cube"

    def __init__(
        self,
        name: str,
        content: list[mk.MkNode] | str | mk.MkNode = "",
        *,
        argument: str = "",
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
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
    def attributes_block(self) -> str:
        """The text block for attributes.

        For subclasses, implement a property for self.attributes.
        """
        if not self.attributes:
            return ""
        lines = [f"    {k}: {v}" for k, v in self.attributes.items() if v is not None]
        return "\n".join(lines) + "\n"

    async def get_content_block(self) -> str:
        """Returns the block content. Can be reimplemented by subclasses."""
        content = await super().get_content()
        return textwrap.indent(content.markdown, self.indent).rstrip("\n") + "\n"

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with block formatting and resources."""
        # Get content from children
        parent_content = await super().get_content()

        # Build the block-formatted markdown
        boundary = self.fence_boundary
        base = f"{boundary} {self.name}"
        if self.argument:
            base += f" | {self.argument}"
        content_text = await self.get_content_block()
        md = f"{base}\n{self.attributes_block}\n{content_text}{boundary}\n"

        return resources.NodeContent(markdown=md, resources=parent_content.resources)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":
    inner_1 = MkBlock("inner_1", content="inner_1 content")
    inner_2 = MkBlock("inner_2", content="inner_2 content")
    outer = MkBlock("outer", content=[inner_1, inner_2])
    print(outer)

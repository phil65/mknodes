from __future__ import annotations

import logging
import textwrap

from typing import Any

from mknodes.basenodes import mkcontainer, mknode


logger = logging.getLogger(__name__)


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
    def content(self):
        return self.items[0]

    def _to_markdown(self) -> str:
        block_level = sum(isinstance(i, MkBlock) for i in self.ancestors)
        block_limiter = "/" * (block_level + 3)
        base = f"{block_limiter} {self.name}"
        if self.argument:
            base += f" | {self.argument}"
        lines = [base]
        lines.extend(f"    {k}: {v}" for k, v in self.attributes.items() if v is not None)
        lines.append("")
        lines.extend(
            (
                textwrap.indent(super()._to_markdown(), self.indent).rstrip("\n"),
                block_limiter,
            ),
        )
        return "\n".join(lines) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "An MkBlock is a base class for pymdownx-style blocks."
        block = MkBlock("html", content="Some text", argument="div")
        page += mknodes.MkCode(str(block), header="Markdown")
        # We can also nest blocks, they will adjust their delimiters automatically.
        page += mknodes.MkHtmlBlock(block, header="Nested")


if __name__ == "__main__":
    inner_1 = MkBlock("inner_1", content="inner_1 content")
    inner_2 = MkBlock("inner_2", content="inner_2 content")
    outer = MkBlock("outer", content=[inner_1, inner_2])
    print(outer)

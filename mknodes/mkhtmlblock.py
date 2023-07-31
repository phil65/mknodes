from __future__ import annotations

import logging
import textwrap

from typing import Any

from mknodes import mkblock, mknode


logger = logging.getLogger(__name__)


class MkHtmlBlock(mkblock.MkBlock):
    """pymdownx-based Html block. Can be used to show raw content."""

    def __init__(
        self,
        content: str | mknode.MkNode = "",
        *,
        attributes: dict[str, str | bool] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: What should be contained in the block
            attributes: Block attrs
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(name="html", argument="div", content=content, **kwargs)

    def _to_markdown(self) -> str:
        block_limiter = "///"
        lines = [f"{block_limiter} {self.name} | {self.argument}"]
        lines.extend(f"    {k}: {v}" for k, v in self.attributes.items())
        lines.append("")
        lines.extend(
            (textwrap.indent(str(self.content), "    ").rstrip("\n"), block_limiter),
        )
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    test = MkHtmlBlock("test")
    print(test)

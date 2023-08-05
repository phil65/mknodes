from __future__ import annotations

import logging
import textwrap

from mknodes.basenodes import mkcontainer


logger = logging.getLogger(__name__)


class MkBlockQuote(mkcontainer.MkContainer):
    """BlockQuote node."""

    ICON = "material/format-quote-open"

    def _to_markdown(self) -> str:
        if any(isinstance(x, MkBlockQuote) for x in self.descendants):
            block_limiter = ""
        else:
            block_level = sum(isinstance(i, MkBlockQuote) for i in self.ancestors)
            block_limiter = ">" * (block_level + 1) + " "
        lines = [
            textwrap.indent(super()._to_markdown(), block_limiter).rstrip(
                "\n",
            ),
        ]
        return "\n".join(lines) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        page += "An MkBlockQuote can display > Blockquotes."
        block = MkBlockQuote(content="Some text")
        page += mknodes.MkReprRawRendered(block, header="### Regular")
        # We can also nest blocks, they will adjust their delimiters automatically.
        nested_quote = MkBlockQuote(block)
        page += mknodes.MkReprRawRendered(nested_quote, header="### Nested")


if __name__ == "__main__":
    inner_1 = MkBlockQuote("inner_1\nmultiline")
    inner_2 = MkBlockQuote("inner_2")
    print(inner_1)
    outer = MkBlockQuote(content=[inner_1, inner_2])
    print(outer)

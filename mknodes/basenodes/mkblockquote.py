from __future__ import annotations

import textwrap

from mknodes.basenodes import mkcontainer
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkBlockQuote(mkcontainer.MkContainer):
    """BlockQuote node."""

    ICON = "material/format-quote-open"
    STATUS = "new"

    def _to_markdown(self) -> str:
        text = super()._to_markdown()
        return textwrap.indent(text, "> ").rstrip("\n") + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "An MkBlockQuote can display > Blockquotes."
        block = MkBlockQuote(content="Some text")
        page += mknodes.MkReprRawRendered(block, header="### Regular")
        # We can also nest blocks, they will adjust their delimiters automatically.
        nested_quote = MkBlockQuote(MkBlockQuote("nested"))
        page += mknodes.MkReprRawRendered(nested_quote, header="### Nested")


if __name__ == "__main__":
    inner_1 = MkBlockQuote("inner_1\nmultiline")
    inner_2 = MkBlockQuote("inner_2")
    outer = MkBlockQuote(content=[inner_1, inner_2, "Not nested"])
    print(outer)

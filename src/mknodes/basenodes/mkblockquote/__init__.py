from __future__ import annotations

import textwrap

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkBlockQuote(mkcontainer.MkContainer):
    """BlockQuote node."""

    ICON = "material/format-quote-open"
    STATUS = "new"

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content and apply blockquote indentation."""
        content = await super().get_content()
        md = textwrap.indent(content.markdown, "> ").rstrip("\n") + "\n"
        return resources.NodeContent(markdown=md, resources=content.resources)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":
    inner_1 = MkBlockQuote("inner_1\nmultiline")
    inner_2 = MkBlockQuote("inner_2")
    outer = MkBlockQuote(content=[inner_1, inner_2, "Not nested"])
    print(outer)

from __future__ import annotations

import logging
import textwrap

from typing import Literal

from markdownizer import markdownnode


logger = logging.getLogger(__name__)


class TabBlock(markdownnode.MarkdownNode):
    REQUIRED_EXTENSIONS = "pymdownx.blocks.tab"

    def __init__(
        self,
        tabs: dict[str, str],
        header: str = "",
    ):
        super().__init__(header=header)
        self.tabs = tabs

    def _to_markdown(self) -> str:
        lines = []
        for k, v in self.tabs.items():
            lines.append(f"/// tab | {k}")
            lines.extend(v.split("\n"))
            lines.append("///\n")
        return "\n".join(lines)


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = TabBlock(tabs)
    print(tabblock)

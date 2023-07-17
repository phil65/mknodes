from __future__ import annotations

from collections.abc import Mapping
import logging

from markdownizer import markdownnode


logger = logging.getLogger(__name__)


class TabBlock(markdownnode.MarkdownNode):
    """pymdownx-based Tab block."""

    REQUIRED_EXTENSIONS = "pymdownx.blocks.tab"

    def __init__(
        self,
        tabs: Mapping[str, str | markdownnode.MarkdownNode],
        header: str = "",
        **kwargs,
    ):
        super().__init__(header=header, **kwargs)
        self.tabs = tabs

    @staticmethod
    def examples():
        yield dict(tabs={"Tab 1": "Some markdown", "Tab 2": "Other Markdown"})

    def _to_markdown(self) -> str:
        lines = []
        for k, v in self.tabs.items():
            lines.append(f"/// tab | {k}")
            lines.extend(str(v).split("\n"))
            lines.append("///\n")
        return "\n".join(lines)


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = TabBlock(tabs)
    print(tabblock)

from __future__ import annotations

from collections.abc import Mapping
import logging
import textwrap

from markdownizer import markdownnode


logger = logging.getLogger(__name__)


class Tabbed(markdownnode.MarkdownNode):
    """pymdownx-based Tab block."""

    REQUIRED_EXTENSIONS = "pymdownx.tabbed"

    def __init__(
        self,
        tabs: Mapping[str, str | markdownnode.MarkdownNode],
        header: str = "",
    ):
        super().__init__(header=header)
        self.tabs = tabs

    @staticmethod
    def examples():
        yield dict(tabs={"Tab 1": "Some markdown", "Tab 2": "Other Markdown"})

    def _to_markdown(self) -> str:
        lines = []
        for k, v in self.tabs.items():
            lines.append(f'=== "{k}"')
            lines.append(textwrap.indent(str(v), prefix="    "))
            lines.append("\n")
        return "\n".join(lines)


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = Tabbed(tabs)
    print(tabblock)

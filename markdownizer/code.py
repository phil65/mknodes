from __future__ import annotations

import logging

from markdownizer import markdownnode


logger = logging.getLogger(__name__)



class Code(markdownnode.Text):
    """Class representing a Code block."""

    def __init__(
        self,
        language: str,
        text: str | markdownnode.MarkdownNode = "",
        *,
        title: str = "",
        header: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        parent=None,
    ):
        super().__init__(text, header=header, parent=parent)
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines

    def _to_markdown(self) -> str:
        title = f" title={self.title}" if self.title else ""
        return f"```{self.language}{title}\n{self.text}\n```"


if __name__ == "__main__":
    section = Code(language="py", text="Some source")
    section.to_markdown()

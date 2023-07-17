from __future__ import annotations

from markdownizer import markdownnode


class MindMap(markdownnode.MarkdownNode):
    """Mermaid Mindmap to display trees."""

    def __init__(self, items: dict, header: str = ""):
        super().__init__(header=header)

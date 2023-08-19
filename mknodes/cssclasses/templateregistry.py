from __future__ import annotations

import markdown

from mknodes.cssclasses import templateblocks


class TemplateRegistry:
    def __init__(self, md: markdown.Markdown):
        self.templates: dict[str, templateblocks.PageTemplate] = {}
        self.md = md

    def __getitem__(self, value):
        return self.templates.setdefault(
            value,
            templateblocks.PageTemplate(self.md, filename=value),
        )

    def __setitem__(self, index, value):
        self.templates[index] = value


if __name__ == "__main__":
    import mknodes

    md = mknodes.Project().config.get_markdown_instance()
    registry = TemplateRegistry(md)
    a = registry["main.html"]
    print(a)

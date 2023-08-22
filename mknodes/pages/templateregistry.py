from __future__ import annotations

import markdown

from mknodes.pages import pagetemplate


class TemplateRegistry:
    def __init__(self, md: markdown.Markdown):
        self.templates: dict[str, pagetemplate.PageTemplate] = {}
        self.md = md

    def __getitem__(self, value: str) -> pagetemplate.PageTemplate:
        return self.templates.setdefault(
            value,
            pagetemplate.PageTemplate(self.md, filename=value),
        )

    def __setitem__(self, index, value):
        self.templates[index] = value

    def __iter__(self):
        return iter(self.templates.values())

    def __len__(self):
        return len(self.templates)


if __name__ == "__main__":
    import mknodes

    proj = mknodes.Project.for_mknodes()
    md = proj.config.get_markdown_instance()
    registry = TemplateRegistry(md)
    a = registry["main.html"]
    for template in registry:
        print(template)

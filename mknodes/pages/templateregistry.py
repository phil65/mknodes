from __future__ import annotations

from mknodes.pages import pagetemplate


class TemplateRegistry:
    def __init__(self):
        self.templates: dict[str, pagetemplate.PageTemplate] = {}

    def __getitem__(self, value: str) -> pagetemplate.PageTemplate:
        return self.templates.setdefault(
            value,
            pagetemplate.PageTemplate(filename=value),
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
    registry = TemplateRegistry()
    a = registry["main.html"]
    for template in registry:
        print(template)

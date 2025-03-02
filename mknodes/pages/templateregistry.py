from __future__ import annotations

from typing import TYPE_CHECKING

from mknodes.pages import pagetemplate


if TYPE_CHECKING:
    from collections.abc import Iterator


class TemplateRegistry:
    def __init__(self):
        self.templates: dict[str, pagetemplate.PageTemplate] = {}

    def __getitem__(self, value: str) -> pagetemplate.PageTemplate:
        return self.templates.setdefault(
            value,
            pagetemplate.PageTemplate(filename=value),
        )

    def __setitem__(self, index: str, value: pagetemplate.PageTemplate):
        self.templates[index] = value

    def __iter__(self) -> Iterator[pagetemplate.PageTemplate]:
        return iter(self.templates.values())

    def __len__(self):
        return len(self.templates)


if __name__ == "__main__":
    registry = TemplateRegistry()
    a = registry["main.html"]
    for template in registry:
        print(template)

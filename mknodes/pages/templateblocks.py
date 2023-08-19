from __future__ import annotations

import dataclasses

from typing import Literal


BlockStr = Literal[
    "analytics",
    "announce",
    "config",
    "container",
    "content",
    "extrahead",
    "fonts",
    "footer",
    "header",
    "hero",
    "htmltitle",
    "libs",
    "outdated",
    "scripts",
    "site_meta",
    "site_nav",
    "styles",
    "tabs",
]


@dataclasses.dataclass
class TemplateBlock:
    name: str
    pre: str
    include_super: bool
    post: str

    def __str__(self):
        super_ = "{{ super() }}" if self.include_super else ""
        text = "{{% block {name} %}}\n{pre}\n{super_}\n{post}\n{{% endblock %}}"
        return text.format(name=self.name, pre=self.pre, super_=super_, post=self.post)


if __name__ == "__main__":
    from mknodes import mkdocsconfig

    cfg = mkdocsconfig.Config()
    md = cfg.get_markdown_instance()

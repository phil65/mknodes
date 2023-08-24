from __future__ import annotations

from collections.abc import Iterable
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


class Block:
    block_id: str

    @property
    def block_content(self):
        raise NotImplementedError

    def __str__(self):
        return f"{{% block {self.block_id} %}}\n{self.block_content}\n{{% endblock %}}"


class HtmlBlock(Block):
    block_id: str

    def __init__(
        self,
        pre: str,
        include_super: bool,
        post: str,
    ):
        self.pre = pre
        self.include_super = include_super
        self.post = post

    def block_content(self):
        super_ = "{{ super() }}" if self.include_super else ""
        return f"{self.pre}\n{super_}\n{self.post}"


class ContentBlock(HtmlBlock):
    block_id = "content"


class AnnouncementBarBlock(HtmlBlock):
    block_id = "announce"


class FooterBlock(HtmlBlock):
    block_id = "announce"


class TitleBlock(Block):
    block_id = "htmltitle"

    def __init__(self, title: str | None = None):
        self.title = title

    def __bool__(self):
        return bool(self.title)

    @property
    def block_content(self):
        return f"<title>{self.title}</title>"


class LibsBlock(Block):
    block_id = "libs"

    def __init__(self, scripts: Iterable[str] | None = None, include_super: bool = True):
        self.include_super = include_super
        self.scripts = set(scripts) if scripts else set()

    def add_script_file(self, script: str):
        self.scripts.add(script)

    def __bool__(self):
        return bool(self.scripts)

    @property
    def block_content(self):
        lines = [
            f'<script src="{{ base_url }}/{path}"></script>' for path in self.scripts
        ]
        scripts = "\n".join(lines)
        return f"{{ super() }}\n{scripts}" if self.include_super else scripts


class StylesBlock(Block):
    block_id = "styles"

    def __init__(self, styles: Iterable[str] | None = None, include_super: bool = True):
        self.include_super = include_super
        self.styles = set(styles) if styles else set()

    def add_stylesheet(self, stylesheet: str):
        self.styles.add(stylesheet)

    def __bool__(self):
        return bool(self.styles)

    @property
    def block_content(self):
        lines = [
            f'<link rel="stylesheet" href="{{ base_url }}/{path}" />'
            for path in self.styles
        ]
        styles = "\n".join(lines)
        return f"{{ super() }}\n{styles}" if self.include_super else styles


if __name__ == "__main__":
    cfg = TitleBlock("a")
    print(cfg)

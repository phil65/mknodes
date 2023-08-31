from __future__ import annotations

from collections.abc import Iterable
from typing import Literal

from markdown import markdown

from mknodes import mkdocsconfig


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


class Super:
    def __str__(self):
        return "{{ super() }}"


class Block:
    block_id: str

    def block_content(self, md: markdown.Markdown | None = None):
        raise NotImplementedError

    def to_markdown(self, md: markdown.Markdown | None = None):
        instance = md or mkdocsconfig.Config().get_markdown_instance()
        content = self.block_content(instance)
        return f"{{% block {self.block_id} %}}\n{content}\n{{% endblock %}}"


class HtmlBlock(Block):
    block_id: str

    def __init__(self):
        self.items = [Super()]

    def __bool__(self):
        return len(self.items) != 1 or not isinstance(self.items[0], Super)

    def block_content(self, md: markdown.Markdown | None = None):
        import mknodes

        instance = md or mkdocsconfig.Config().get_markdown_instance()
        result = ""
        for i in self.items:
            match i:
                case mknodes.MkNode():
                    result += instance.convert(str(i))
                case _:
                    result += str(i)
            result += "\n"
        return result

    @property
    def content(self):
        return self.items[0]

    @content.setter
    def content(self, value):
        self.items = [value]


class ContentBlock(HtmlBlock):
    block_id = "content"


class AnnouncementBarBlock(HtmlBlock):
    block_id = "announce"


class FooterBlock(HtmlBlock):
    block_id = "footer"


class TabsBlock(HtmlBlock):
    block_id = "tabs"


class TitleBlock(Block):
    block_id = "htmltitle"

    def __init__(self, title: str | None = None):
        self.title = title

    def __bool__(self):
        return bool(self.title)

    def block_content(self, md: markdown.Markdown | None = None):
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

    def block_content(self, md: markdown.Markdown | None = None):
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

    def block_content(self, md: markdown.Markdown | None = None):
        lines = [
            f'<link rel="stylesheet" href="{{ base_url }}/{path}" />'
            for path in self.styles
        ]
        styles = "\n".join(lines)
        return f"{{ super() }}\n{styles}" if self.include_super else styles


if __name__ == "__main__":
    cfg = AnnouncementBarBlock()
    print(cfg.to_markdown())

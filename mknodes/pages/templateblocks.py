from __future__ import annotations

from typing import Literal

from markdown import markdown

from mknodes.basenodes import mknode
from mknodes.utils import requirements


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
        return "{{{{ super() }}}}"


class Block(mknode.MkNode):
    block_id: str

    def block_content(self, md: markdown.Markdown | None = None):
        raise NotImplementedError

    def to_markdown(self, md: markdown.Markdown | None = None):
        from mknodes import mkdocsconfig

        instance = md or mkdocsconfig.Config().get_markdown_instance()
        content = self.block_content(instance)
        return f"{{% block {self.block_id} %}}\n{content}\n{{% endblock %}}"


class HtmlBlock(Block):
    block_id: str

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.items = [Super()]

    def __bool__(self):
        return len(self.items) != 1 or not isinstance(self.items[0], Super)

    def block_content(self, md: markdown.Markdown | None = None) -> str:
        import mknodes

        from mknodes import mkdocsconfig

        instance = md or mkdocsconfig.Config().get_markdown_instance()
        result = ""
        for i in self.items:
            match i:
                case mknodes.MkNode():
                    i.parent = self.parent
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
        value = self.to_child_node(value)
        self.items = [value]


class ContentBlock(HtmlBlock):
    block_id = "content"


class AnnouncementBarBlock(HtmlBlock):
    block_id = "announce"


class FooterBlock(HtmlBlock):
    block_id = "footer"


class OutdatedBlock(HtmlBlock):
    block_id = "outdated"


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

    def __init__(
        self,
        scripts: list[requirements.JSFile | requirements.JSLink] | None = None,
        include_super: bool = True,
    ):
        self.include_super = include_super
        self.scripts = scripts or []

    def add_script_file(self, script: requirements.JSFile | requirements.JSLink):
        self.scripts.append(script)

    def __bool__(self):
        return bool(self.scripts)

    def block_content(self, md: markdown.Markdown | None = None):
        lines = [i.to_html() for i in self.scripts]
        scripts = "\n".join(lines)
        return f"{{{{ super() }}}}\n{scripts}" if self.include_super else scripts


class StylesBlock(Block):
    block_id = "styles"

    def __init__(
        self,
        styles: list[requirements.CSSLink] | None = None,
        include_super: bool = True,
    ):
        self.include_super = include_super
        self.styles = styles or []

    def add_stylesheet(self, stylesheet: requirements.CSSLink):
        self.styles.append(stylesheet)

    def __bool__(self):
        return bool(self.styles)

    def block_content(self, md: markdown.Markdown | None = None):
        lines = [i.to_html() for i in self.styles]
        styles = "\n".join(lines)
        return f"{{{{ super() }}}}\n{styles}" if self.include_super else styles


if __name__ == "__main__":
    cfg = AnnouncementBarBlock()
    print(cfg.to_markdown())

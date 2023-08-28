from __future__ import annotations

import markdown

from mknodes.pages import templateblocks
from mknodes.utils import helpers


class PageTemplate:
    def __init__(
        self,
        md: markdown.Markdown,
        filename: str,
        extends: str | None = "base",
    ):
        self.filename = filename
        self.extends = extends
        self.md = md
        self.title_block = templateblocks.TitleBlock()
        self.content_block = templateblocks.ContentBlock(md)
        self.announce_block = templateblocks.AnnouncementBarBlock(md)
        self.footer_block = templateblocks.FooterBlock(md)
        self.libs_block = templateblocks.LibsBlock()
        self.styles_block = templateblocks.StylesBlock()

    @property
    def blocks(self):
        return [
            self.title_block,
            self.content_block,
            self.announce_block,
            self.footer_block,
            self.libs_block,
            self.styles_block,
        ]

    def __repr__(self):
        return helpers.get_repr(
            self,
            filename=self.filename,
            extends=self.extends,
            _filter_empty=True,
        )

    @property
    def announcement_bar(self):
        return self.announce_block.content

    @announcement_bar.setter
    def announcement_bar(self, value):
        self.announce_block.content = value

    @property
    def content(self):
        return self.content_block.content

    @content.setter
    def content(self, value):
        self.content_block.content = value

    def build_html(self) -> str | None:
        blocks = ['{% extends "' + self.extends + '.html" %}\n'] if self.extends else []
        blocks.extend(str(block) for block in self.blocks if block)
        return "\n".join(blocks) + "\n" if blocks else None


if __name__ == "__main__":
    import mknodes

    from mknodes import mkdocsconfig

    cfg = mkdocsconfig.Config()
    md = cfg.get_markdown_instance()
    template = PageTemplate(md, filename="main.html")
    template.announce_block.content = mknodes.MkAdmonition("test")
    html = template.build_html()
    print(html)

from __future__ import annotations

from typing import TYPE_CHECKING

from mknodes.mdlib import mdconverter
from mknodes.pages import templateblocks
from mknodes.utils import reprhelpers


if TYPE_CHECKING:
    import markdown

    import mknodes as mk


class PageTemplate:
    """A jinja template used to build a website from an MkPage."""

    def __init__(
        self,
        filename: str | None = None,
        *,
        extends: str | None = "base.html",
        parent: mk.MkPage | mk.MkNav | None = None,
    ):
        """Constructor.

        Arguments:
            filename: Optional filename for the Template (can get overridden during build)
            extends: Parent template path
            parent: The MkPage using this Page template.
        """
        self.filename = filename
        self.extends = f"{extends.rstrip('.html')}.html" if extends else None
        self.parent = parent

        # Common blocks
        self.title = templateblocks.TitleBlock()
        self.libs = templateblocks.LibsBlock()
        self.analytics = templateblocks.AnalyticsBlock()
        self.scripts = templateblocks.ScriptsBlock()
        self.site_meta = templateblocks.SiteMetaBlock()
        self.styles = templateblocks.StylesBlock()
        self.extra_head = templateblocks.ExtraHeadBlock()

        self.content_block = templateblocks.HtmlBlock("content", parent=parent)
        self.footer = templateblocks.HtmlBlock("footer", parent=parent)
        self.site_nav = templateblocks.HtmlBlock("site_nav", parent=parent)

        # MkDocs-Material
        self.tabs = templateblocks.HtmlBlock("tabs", parent=parent)
        self.outdated = templateblocks.HtmlBlock("outdated", parent=parent)
        self.hero = templateblocks.HtmlBlock("hero", parent=parent)
        self.announce = templateblocks.HtmlBlock("announce", parent=parent)

    def __bool__(self):
        return any(self.blocks)  # or self.extends

    def __hash__(self):
        return hash(self.build_html())

    @property
    def blocks(self) -> list[templateblocks.BaseBlock]:
        """A list containing all blocks of the PageTemplate."""
        return [
            self.title,
            self.content_block,
            self.tabs,
            self.announce,
            self.footer,
            self.libs,
            self.styles,
            self.outdated,
            self.hero,
            self.extra_head,
            self.site_nav,
            self.analytics,
            self.site_meta,
            self.scripts,
        ]

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            filename=self.filename,
            extends=self.extends,
            _filter_empty=True,
        )

    @property
    def announcement_bar(self):
        return self.announce.content

    @announcement_bar.setter
    def announcement_bar(self, value):
        import mknodes as mk

        if isinstance(value, mk.MkNode):
            value._ctx = self.parent.ctx
        self.announce.content = value

    @property
    def content(self):
        return self.content_block.content

    @content.setter
    def content(self, value):
        self.content_block.content = value

    def build_html(self, md: markdown.Markdown | None = None) -> str | None:
        """Convert given PageTemplate to HTML.

        Arguments:
            md: Markdown parser to use for HTML conversion.
        """
        md = md or mdconverter.MdConverter()
        blocks = [r'{% extends "' + self.extends + '" %}\n'] if self.extends else []
        blocks.extend(block.to_markdown(md) for block in self.blocks if block)
        return "\n".join(blocks) + "\n" if blocks else None


if __name__ == "__main__":
    import mknodes as mk

    md = mdconverter.MdConverter()
    template = PageTemplate(filename="main.html")
    template.announce.content = mk.MkAdmonition("test")
    html = template.build_html(md)
    print(html)

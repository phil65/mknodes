from __future__ import annotations

import os

from typing import TYPE_CHECKING, Literal

from jinjarope import envglobals

from mknodes.basenodes import mknode
from mknodes.mdlib import mdconverter
from mknodes.utils import helpers, resources


if TYPE_CHECKING:
    import markdown

    import mknodes as mk


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


SUPER_TEXT = r"{{ super() }}"

REDIRECT = """
<link rel="canonical" href="{url}">
<meta name="robots" content="noindex">
<script>var anchor=window.location.hash.substr(1);location.href="{url}"+(anchor?"#"+anchor:"")</script>
<meta http-equiv="refresh" content="0; url={url}">
"""


class Super:
    """Simple class to use for the jinja super expression."""

    def __str__(self):
        return SUPER_TEXT


class BaseBlock(mknode.MkNode):
    """A class representing a block from a page template."""

    block_id: str

    def block_content(self, md: markdown.Markdown | None = None):
        raise NotImplementedError

    def to_markdown(self, md: markdown.Markdown | None = None):
        """Return HTML for the block.

        Arguments:
            md: Markdown parser to use
        """
        instance = md or mdconverter.MdConverter()
        content = self.block_content(instance)
        return f"{{% block {self.block_id} %}}\n{content}\n{{% endblock %}}"


class HtmlBlock(BaseBlock):
    """Base class for blocks which usually contain HTML content."""

    def __init__(self, block_id: str, *, parent: mk.MkPage | mk.MkNav | None = None):
        """Constructor.

        Arguments:
            block_id: Name of the block
            parent: Parent node
        """
        super().__init__(parent=parent)
        self.block_id = block_id
        self.items = [Super()]

    def __bool__(self):
        return len(self.items) != 1 or not isinstance(self.items[0], Super)

    def block_content(self, md: markdown.Markdown | None = None) -> str:
        """Return the actual block content.

        Arguments:
            md: Markdown parser to use
        """
        import mknodes as mk

        instance = md or mdconverter.MdConverter()
        result = ""
        for i in self.items:
            match i:
                case mk.MkNode():
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


class Block(BaseBlock):
    """Base class for head blocks."""

    def __init__(self):
        self.content = ""

    def __bool__(self):
        return bool(self.block_content())

    def block_content(self, md: markdown.Markdown | None = None):
        return self.content


class TitleBlock(BaseBlock):
    """Block wrapping the HTML title."""

    block_id = "htmltitle"

    def __init__(self, content: str | None = None):
        self.content = content

    def __bool__(self):
        return bool(self.content)

    def block_content(self, md: markdown.Markdown | None = None):
        return f"<title>{self.content}</title>"


class BaseJSBlock(BaseBlock):
    """Block for additional libraries."""

    def __init__(
        self,
        scripts: list[resources.JSFile] | None = None,
        include_super: bool = True,
    ):
        """Constructor.

        Arguments:
            scripts: List of scripts to add to HTML header libs.
            include_super: Whether to include the original content.
        """
        self.include_super = include_super
        self.scripts = scripts or []

    def add_script_file(self, script: resources.JSFile | str | os.PathLike):
        """Add a script file to the block.

        Arguments:
            script: Script to add to the block
        """
        if isinstance(script, str | os.PathLike):
            script = resources.JSFile(str(script))
        self.scripts.append(script)

    def __bool__(self):
        return bool(self.scripts)

    def block_content(self, md: markdown.Markdown | None = None):
        lines = [i.to_html() for i in self.scripts]
        scripts = "\n".join(lines)
        return f"{SUPER_TEXT}\n{scripts}" if self.include_super else scripts


class LibsBlock(BaseJSBlock):
    """Block for additional libraries."""

    block_id = "libs"


class ScriptsBlock(BaseJSBlock):
    """Block for JavaScripts at end of BODY."""

    block_id = "scripts"


class AnalyticsBlock(Block):
    """Block for analytics-tags in HEAD."""

    block_id = "analytics"


class SiteMetaBlock(Block):
    """Block for meta tags in HEAD."""

    block_id = "site_meta"


class ExtraHeadBlock(Block):
    """Block for extra HEAD content.

    Can be used for stuff not covered by other blocks, like changing the
    indexing rules.
    """

    block_id = "extrahead"

    def __init__(self):
        super().__init__()
        self.robots_rule = None
        self.redirect_url = None

    def block_content(self, md: markdown.Markdown | None = None):
        content = self.content
        if self.robots_rule:
            rule = f'\n<meta name="robots" content="{self.robots_rule}">'
            content += rule
        if self.redirect_url:
            content += REDIRECT.format(url=self.redirect_url)
        return content

    def set_robots_rule(self, rule: str | None = None):
        """Set a rule for search robots.

        For valid rule values, check
        https://developers.google.com/search/docs/crawling-indexing/robots-meta-tag

        Arguments:
            rule: Rule to apply for robots
        """
        self.robots_rule = rule

    def set_redirect_url(self, url: str):
        """Set a URL which the page should redirect to.

        Arguments:
            url: URL to redirect to
        """
        self.redirect_url = url


class StylesBlock(BaseBlock):
    """Block for additional stylesheets."""

    block_id = "styles"

    def __init__(
        self,
        styles: list[resources.CSSFile | resources.CSSText] | None = None,
        include_super: bool = True,
    ):
        self.include_super = include_super
        self.styles = styles or []

    def add_stylesheet(self, stylesheet: resources.CSSFile):
        self.styles.append(stylesheet)

    def add_css(self, css: str | dict):
        """Add CSS in form of a string or a CSS-rule like dictionary.

        Arguments:
            css: A string or dict containing CSS
        """
        css_str = envglobals.format_css_rule(css) if isinstance(css, dict) else css
        filename = f"{helpers.get_hash(css_str)}.css"
        text = resources.CSSText(filename=filename, content=css_str)
        self.styles.append(text)

    def __bool__(self):
        return bool(self.styles)

    def block_content(self, md: markdown.Markdown | None = None):
        lines = [i.to_html() for i in self.styles]
        styles = "\n".join(lines)
        return f"{SUPER_TEXT}\n{styles}" if self.include_super else styles


if __name__ == "__main__":
    block = StylesBlock()
    print(block.to_markdown())

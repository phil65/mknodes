"""Markdown -> HTML per flavour (`MkNode.to_html()`, the "Html" tab of node examples).

Every flavour needs a parser that knows its syntax, otherwise the HTML shows raw markers
(`[!WARNING]`, `:::{note}`):

- material: Python-Markdown with the extensions the nodes require (pymdown etc.).
- github / mdbook: comrak via `mkconvert` (GFM + alerts + footnotes), the parser closest to
  GitHub's own renderer. mdBook's optional `mdbook-admonish` blocks stay code blocks,
  since they are rendered by an mdBook preprocessor.
- myst: markdown-it-py with the MyST plugins (`colon_fence`, roles, targets) plus a small
  mapping of the directives mknodes writes (admonitions, `{dropdown}`, `{tab-set}` /
  `{tab-item}`, `{code-block}`) to HTML resembling Sphinx's. Real MyST output needs
  Sphinx (directives are docutils nodes), so this is an approximation for previews.
  Roles (`` {ref}`x` ``) keep their text.

The comrak / markdown-it-py parsers come with the `html` extra (`mknodes[html]`); without
it, the HTML is rendered with Python-Markdown and starts with a comment saying so.
"""

import html
import re
from typing import TYPE_CHECKING, Any

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Sequence

    from markdown_it import MarkdownIt
    from markdown_it.token import Token

    from mknodes.utils import resources


logger = log.get_logger(__name__)

DIRECTIVE_RE = re.compile(r"^\{(?P<name>[\w-]+)\}\s*(?P<argument>.*)$")
OPTION_RE = re.compile(r"^:(?P<key>[\w-]+):\s*(?P<value>.*)$")
# MyST admonition directives (docutils admonitions + `seealso`).
ADMONITIONS = {
    "note",
    "tip",
    "hint",
    "important",
    "attention",
    "caution",
    "warning",
    "error",
    "danger",
    "seealso",
}
ADMONITION_TITLES = {"seealso": "See also"}


def fallback_note(flavor: str, extra: str) -> str:
    """Return the HTML comment marking HTML rendered without the flavour's parser."""
    return (
        f"<!-- {flavor} flavour: {extra} not installed (`pip install mknodes[html]`), "
        "rendered with Python-Markdown, flavour syntax may show up raw -->\n"
    )


def python_markdown(markdown: str, reqs: resources.Resources | None = None) -> str:
    """Render Material flavoured Markdown with Python-Markdown + required extensions."""
    from mknodes.mdlib import mdconverter

    configs = reqs.markdown_extensions if reqs else {}
    converter = mdconverter.MdConverter(extensions=list(configs), extension_configs=configs)
    return converter.convert(markdown)


def comrak(markdown: str, reqs: resources.Resources | None = None, flavor: str = "github") -> str:
    """Render GitHub flavoured Markdown (alerts, footnotes, raw HTML) with comrak."""
    try:
        from mkconvert import ComrakParser, MarkdownOptions
    except ImportError:
        return fallback_note(flavor, "mkconvert") + python_markdown(markdown, reqs)
    if not ComrakParser.is_available():
        return fallback_note(flavor, "comrak") + python_markdown(markdown, reqs)
    options = MarkdownOptions.gfm(alerts=True, footnotes=True, raw_html=True, heading_ids=True)
    parser = ComrakParser(options)
    return parser.convert(markdown)


def myst(markdown: str, reqs: resources.Resources | None = None) -> str:
    """Render MyST Markdown with markdown-it-py (directives mapped to HTML)."""
    try:
        md = _myst_parser()
    except ImportError:
        return fallback_note("myst", "markdown-it-py / mdit-py-plugins") + python_markdown(
            markdown, reqs
        )
    return md.render(markdown)


def _myst_parser() -> MarkdownIt:
    from markdown_it import MarkdownIt
    from mdit_py_plugins.colon_fence import colon_fence_plugin
    from mdit_py_plugins.deflist import deflist_plugin
    from mdit_py_plugins.footnote import footnote_plugin
    from mdit_py_plugins.front_matter import front_matter_plugin
    from mdit_py_plugins.myst_blocks import myst_block_plugin
    from mdit_py_plugins.myst_role import myst_role_plugin
    from mdit_py_plugins.tasklists import tasklists_plugin

    md = MarkdownIt("commonmark", {"html": True}).enable(["table", "strikethrough"])
    for plugin in (
        front_matter_plugin,
        myst_block_plugin,
        myst_role_plugin,
        colon_fence_plugin,
        deflist_plugin,
        footnote_plugin,
        tasklists_plugin,
    ):
        md.use(plugin)
    rules = md.renderer.rules  # type: ignore[attr-defined]
    default_fence, default_colon_fence = rules["fence"], rules["colon_fence"]

    def render_fence(self: Any, tokens: Sequence[Token], idx: int, options: Any, env: Any) -> str:
        token = tokens[idx]
        default = default_colon_fence if token.type == "colon_fence" else default_fence
        match = DIRECTIVE_RE.match(token.info.strip())
        if not match:
            return default(tokens, idx, options, env)
        name, argument = match["name"], match["argument"].strip()
        opts, body = _split_options(token.content)
        return _directive(md, name, argument, opts, body, env)

    def render_role(self: Any, tokens: Sequence[Token], idx: int, options: Any, env: Any) -> str:
        return f"<code>{html.escape(tokens[idx].content)}</code>"

    def render_target(self: Any, tokens: Sequence[Token], idx: int, options: Any, env: Any) -> str:
        return f'<span id="{html.escape(tokens[idx].content)}"></span>\n'

    md.add_render_rule("fence", render_fence)
    md.add_render_rule("colon_fence", render_fence)
    md.add_render_rule("myst_role", render_role)
    md.add_render_rule("myst_target", render_target)
    return md


def _split_options(content: str) -> tuple[dict[str, str], str]:
    """Split the leading `:key: value` option lines of a directive from its body."""
    lines = content.splitlines()
    opts: dict[str, str] = {}
    i = 0
    while i < len(lines) and (match := OPTION_RE.match(lines[i])):
        opts[match["key"]] = match["value"].strip()
        i += 1
    return opts, "\n".join(lines[i:])


def _directive(  # noqa: PLR0911
    md: MarkdownIt,
    name: str,
    argument: str,
    opts: dict[str, str],
    body: str,
    env: Any,
) -> str:
    """Return HTML for a MyST directive (structure like Sphinx / sphinx-design output)."""
    esc = html.escape
    match name:
        case "code-block" | "code" | "sourcecode":
            lang = f' class="language-{esc(argument)}"' if argument else ""
            code = f"<pre><code{lang}>{esc(body.strip(chr(10)) + chr(10))}</code></pre>\n"
            if caption := opts.get("caption"):
                return (
                    f'<div class="literal-block-wrapper"><div class="code-block-caption">'
                    f"{esc(caption)}</div>\n{code}</div>\n"
                )
            return code
        case _ if name in ADMONITIONS:
            title = ADMONITION_TITLES.get(name, name.capitalize())
            if argument:  # an argument is the first paragraph of the content
                body = f"{argument}\n\n{body}"
            return _admonition(name, title, md.render(body, env))
        case "admonition":
            classes = opts.get("class", "")
            return _admonition(classes, argument, md.render(body, env))
        case "dropdown":
            attr = " open" if "open" in opts else ""
            classes = "sd-dropdown"
            if color := opts.get("color"):
                classes += f" sd-bg-{esc(color)}"
            return (
                f'<details class="{classes}"{attr}>\n<summary>{md.renderInline(argument)}'
                f"</summary>\n{md.render(body, env)}</details>\n"
            )
        case "tab-set":
            return f'<div class="sd-tab-set">\n{md.render(body, env)}</div>\n'
        case "tab-item":
            return (
                f'<div class="sd-tab-item">\n<p class="sd-tab-label">'
                f"{md.renderInline(argument)}</p>\n{md.render(body, env)}</div>\n"
            )
        case _:
            title = f"<p>{md.renderInline(argument)}</p>\n" if argument else ""
            return f'<div class="{esc(name)}">\n{title}{md.render(body, env)}</div>\n'


def _admonition(classes: str, title: str, body: str) -> str:
    cls = f"admonition {html.escape(classes)}".strip()
    return (
        f'<div class="{cls}">\n<p class="admonition-title">{html.escape(title)}</p>\n{body}</div>\n'
    )

"""GitHub flavour: GFM plus GitHub alerts and the HTML GitHub renders.

Nodes without a rule here (and without an `[output.github]` template in their node
file) render their default (Material) Markdown.
"""

from __future__ import annotations

import html
from typing import TYPE_CHECKING
import urllib.parse

import griffe

import mknodes as mk
from mknodes.basenodes import processors
from mknodes.rendering import apidocs, base, materialtext
from mknodes.utils import log


if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    from mknodes.build.output import BuildOutput


logger = log.get_logger(__name__)

# Admonition type -> GitHub alert type (GitHub only knows these five).
ALERT_TYPES = {
    "note": "NOTE",
    "abstract": "NOTE",
    "info": "NOTE",
    "example": "NOTE",
    "quote": "NOTE",
    "tip": "TIP",
    "success": "TIP",
    "question": "TIP",
    "important": "IMPORTANT",
    "warning": "WARNING",
    "failure": "CAUTION",
    "danger": "CAUTION",
    "bug": "CAUTION",
}

PROGRESS_WIDTH = 10


class GithubRenderer(base.Renderer):
    """Renders GitHub flavoured Markdown (READMEs, issues, wikis)."""

    name = "github"
    template_key = "github"

    def processors(self, node: mknode.MkNode) -> list[processors.TextProcessor]:
        result: list[processors.TextProcessor] = []
        for proc in node.get_processors():
            match proc:
                case processors.AppendCssClassesProcessor():
                    pass  # GitHub has no attribute lists
                case processors.PrependMetadataProcessor():
                    # GitHub shows front matter as a table: use the title only.
                    if title := proc.meta.title:
                        result.append(PrependTitleProcessor(title))
                case _:
                    result.append(proc)
        if isinstance(node, mk.MkPage):
            result.append(MaterialTextProcessor())
        return result

    def finalize(self, output: BuildOutput, root: mk.MkNav) -> None:
        """Link `[title][dotted.path]` references (GitHub has no autorefs)."""
        from mknodes.build import refcheck

        refcheck.link_references(output, inventory=root.ctx.links.inv_manager)


def _material_admonition(adm: materialtext.Admonition) -> str:
    if adm.collapsible:
        return details(adm.title or adm.typ.capitalize(), adm.text, open_=adm.expanded)
    return alert(adm.typ, adm.text, adm.title)


def _material_tabs(tabs: list[materialtext.Tab]) -> str:
    selected = next((i for i, tab in enumerate(tabs) if tab.selected), 0)
    return "\n".join(
        details(tab.title, tab.text, open_=i == selected) for i, tab in enumerate(tabs)
    )


MATERIAL_CONVERTERS = materialtext.Converters(
    admonition=_material_admonition,
    tabs=_material_tabs,
)


class MaterialTextProcessor(processors.TextProcessor):
    """Convert hand-written Material blocks (admonitions, tabs) of a page."""

    ID = "material_text"

    def run(self, text: str) -> str:
        return materialtext.convert(text, MATERIAL_CONVERTERS)


class PrependTitleProcessor(processors.TextProcessor):
    """Prepend a `# title` heading unless the text already starts with one."""

    ID = "prepend_title"

    def __init__(self, title: str) -> None:
        self.title = title

    def run(self, text: str) -> str:
        if text.lstrip().startswith("# "):
            return text
        return f"# {self.title}\n\n{text}"


def quote(text: str) -> str:
    """Prefix every line with `> ` (blank lines with `>`)."""
    return "\n".join(f"> {line}" if line else ">" for line in text.splitlines())


def alert(typ: str, text: str, title: str | None = None) -> str:
    """Return a GitHub alert block (`> [!NOTE]`)."""
    kind = ALERT_TYPES.get(typ, "NOTE")
    body = f"**{title}**\n\n{text}" if title else text
    return f"> [!{kind}]\n{quote(body.strip())}\n"


def details(summary: str, text: str, *, open_: bool = False) -> str:
    """Return a collapsible `<details>` block (Markdown content needs blank lines)."""
    tag = "<details open>" if open_ else "<details>"
    return f"{tag}\n<summary>{html.escape(summary)}</summary>\n\n{text.strip()}\n\n</details>\n"


@GithubRenderer.rule(mk.MkAdmonition)
async def render_admonition(node: mk.MkAdmonition, r: base.Renderer) -> str:
    if not node.title and not node.get_items():
        return ""
    text = await r.render_children(node.get_items())
    if node.annotations:
        text = f"{text}\n\n{await r.render_markdown(node.annotations)}"
    if node.collapsible:
        summary = node.title or node.typ.capitalize()
        return details(summary, text, open_=bool(node.expanded))
    return alert(node.typ, text, node.title)


@GithubRenderer.rule(mk.MkCompactAdmonition)
async def render_compact_admonition(node: mk.MkCompactAdmonition, r: base.Renderer) -> str:
    text = await node.get_text()
    if isinstance(text, mk.MkNode):
        text = (await r.render_child(text)).markdown
    return alert(node.typ or "note", text)


@GithubRenderer.rule(mk.MkDetailsBlock)
async def render_details_block(node: mk.MkDetailsBlock, r: base.Renderer) -> str:
    text = await r.render_children(node.get_items())
    return details(node.title or node.typ.capitalize(), text, open_=bool(node.expanded))


@GithubRenderer.rule(mk.MkBlock)
async def render_block(node: mk.MkBlock, r: base.Renderer) -> str:
    """Unknown PyMdown blocks: keep the content, drop the block."""
    return await r.render_children(node.get_items())


@GithubRenderer.rule(mk.MkTab, mk.MkTabBlock)
async def render_tab(node: mk.MkTab | mk.MkTabBlock, r: base.Renderer) -> str:
    text = await r.render_children(node.get_items())
    return details(node.title, text, open_=bool(node.select))


@GithubRenderer.rule(mk.MkTabContainer)
async def render_tab_container(node: mk.MkTabContainer, r: base.Renderer) -> str:
    """Tabs become `<details>` blocks, the selected (or first) one expanded."""
    tabs = node.get_items()
    if not tabs:
        return ""
    selected = node.select_tab if node.select_tab is not None else 0
    if isinstance(selected, str):
        selected = node._get_tab_pos(selected)
    parts = []
    for i, tab in enumerate(tabs):
        text = await r.render_children(tab.get_items())
        parts.append(details(tab.title, text, open_=i == selected))
    return "\n".join(parts)


@GithubRenderer.rule(mk.MkCode)
async def render_code(node: mk.MkCode, r: base.Renderer) -> str:
    """Fenced code block with plain language info string (no attributes)."""
    text = await node.get_text()
    fence = node.fence_for(text)
    code = f"{fence}{node.language or ''}\n{text}\n{fence}"
    return f"**{node.title}**\n\n{code}" if node.title else code


@GithubRenderer.rule(mk.MkKeys)
async def render_keys(node: mk.MkKeys, r: base.Renderer) -> str:
    return "+".join(f"<kbd>{html.escape(key.capitalize())}</kbd>" for key in node.keys)


CRITIC_TAGS = {"addition": "ins", "deletion": "del", "highlight": "mark"}


@GithubRenderer.rule(mk.MkCritic)
async def render_critic(node: mk.MkCritic, r: base.Renderer) -> str:
    text = await r.render_children(node.get_items())
    if node.typ == "comment":
        return f"<!-- {text} -->"
    tag = CRITIC_TAGS[node.typ]
    return f"<{tag}>\n\n{text}\n\n</{tag}>"


@GithubRenderer.rule(mk.MkProgressBar)
async def render_progress_bar(node: mk.MkProgressBar, r: base.Renderer) -> str:
    filled = round(node.percentage / 100 * PROGRESS_WIDTH)
    bar = "█" * filled + "░" * (PROGRESS_WIDTH - filled)
    label = f" {node.label}" if node.label else ""
    return f"`{bar}`{label}"


@GithubRenderer.rule(mk.MkDefinitionList)
async def render_definition_list(node: mk.MkDefinitionList, r: base.Renderer) -> str:
    items = []
    for key, value in node.data.items():
        if isinstance(value, mk.MkNode):
            value = (await r.render_child(value)).markdown
        text = value
        items.append(f"<dt>{html.escape(key)}</dt>\n<dd>\n\n{text.strip()}\n\n</dd>")
    return "<dl>\n" + "\n".join(items) + "\n</dl>\n"


@GithubRenderer.rule(mk.MkDocStrings)
async def render_docstrings(node: mk.MkDocStrings, r: base.Renderer) -> str:
    """API docs rendered from Griffe (GitHub has no mkdocstrings)."""
    from mknodes.info import grifferegistry

    if isinstance(node.obj, griffe.Object):
        obj: griffe.Object | griffe.Alias = node.obj
    else:
        try:
            obj = grifferegistry.registry.get_module(node.obj_path)
        except (KeyError, ImportError, griffe.AliasResolutionError) as e:
            logger.warning("Could not load API docs for %s: %s", node.obj_path, e)
            return f"`{node.obj_path}`"
    try:
        return apidocs.render(obj, node.options)
    except (griffe.AliasResolutionError, griffe.CyclicAliasError) as e:
        logger.warning("Could not render API docs for %s: %s", node.obj_path, e)
        return f"`{node.obj_path}`"


ICONIFY_URL = "https://api.iconify.design/{prefix}/{name}.svg"


def icon_img(icon: str, *, height: str | int = 16, color: str | None = None) -> str:
    """Return an `<img>` of an Iconify icon (GitHub strips inline SVG and has no shortcodes)."""
    from jinjarope import iconfilters

    prefix, _, name = iconfilters.get_pyconify_key(icon).partition(":")
    params = {"height": str(height).removesuffix("px")}
    if color:
        params["color"] = color
    url = ICONIFY_URL.format(prefix=prefix, name=name)
    return f'<img src="{url}?{urllib.parse.urlencode(params)}" alt="{html.escape(name)}">'


@GithubRenderer.rule(mk.MkLink)
async def render_link(node: mk.MkLink, r: base.Renderer) -> str:
    prefix = f"{icon_img(node._icon)} " if node._icon else ""
    tooltip = f' "{node.tooltip}"' if node.tooltip else ""
    return f"[{prefix}{await node.get_title()}]({await node.get_url()}{tooltip})"


@GithubRenderer.rule(mk.MkIcon)
async def render_icon(node: mk.MkIcon, r: base.Renderer) -> str:
    return icon_img(node.icon_name, height=node.height or 24, color=node.color)


@GithubRenderer.rule(mk.MkMaterialBadge)
async def render_material_badge(node: mk.MkMaterialBadge, r: base.Renderer) -> str:
    icon = icon_img(node.icon) if node.icon else ""
    content = f"{icon} <code>{html.escape(await node.get_text())}</code>".strip()
    if not node.target:
        return content
    url = await mk.MkLink(node.target, parent=node).get_url()
    return f"[{content}]({url})"

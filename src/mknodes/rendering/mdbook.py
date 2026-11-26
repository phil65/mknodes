"""mdBook flavour: the GitHub flavour plus optional `mdbook-admonish` admonitions.

mdBook (>= 0.5) renders CommonMark with GitHub's extensions, including GitHub alerts
(`> [!NOTE]`), raw HTML (`<details>`, `<kbd>`, `<img>`) and `.md` links (turned into
`.html`). So by default the output equals the GitHub flavour. With `admonish=True`,
admonitions use the fenced syntax of the `mdbook-admonish` preprocessor
(all Material admonition types, titles, collapsible blocks).
"""

import dataclasses
from typing import TYPE_CHECKING

import mknodes as mk
from mknodes.basenodes.mkcode import INNER_FENCE_RE
from mknodes.rendering import github, materialtext


if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    from mknodes.basenodes.processors import TextProcessor
    from mknodes.rendering import base


# Material admonition type -> mdbook-admonish directive (it knows the Material types,
# plus a few aliases).
ADMONISH_TYPES = {
    "note",
    "abstract",
    "info",
    "tip",
    "success",
    "question",
    "warning",
    "failure",
    "danger",
    "bug",
    "example",
    "quote",
}


def admonish(
    typ: str,
    text: str,
    title: str | None = None,
    *,
    collapsible: bool = False,
) -> str:
    """Return an `mdbook-admonish` block (fence longer than fences in the text)."""
    directive = typ if typ in ADMONISH_TYPES else "note"
    inner = max((len(i) for i in INNER_FENCE_RE.findall(text)), default=0)
    fence = "`" * max(3, inner + 1)
    attrs = ""
    if title:
        escaped = title.replace('"', '\\"')
        attrs += f' title="{escaped}"'
    if collapsible:
        attrs += " collapsible=true"
    return f"{fence}admonish {directive}{attrs}\n{text.strip()}\n{fence}\n"


def _material_admonition(adm: materialtext.Admonition) -> str:
    return admonish(adm.typ, adm.text, adm.title, collapsible=adm.collapsible)


def _material_block(block: materialtext.Block) -> str:
    if block.name == "admonition" or block.name in ADMONISH_TYPES:
        typ = "note" if block.name == "admonition" else block.name
        return admonish(typ, block.text, block.argument)
    if block.name == "details":
        return admonish("note", block.text, block.argument or "Details", collapsible=True)
    return github.material_block(block)


ADMONISH_CONVERTERS = dataclasses.replace(
    github.MATERIAL_CONVERTERS,
    admonition=_material_admonition,
    block=_material_block,
)


class AdmonishTextProcessor(github.MaterialTextProcessor):
    """Convert hand-written Material blocks, admonitions into `mdbook-admonish` blocks."""

    ID = "admonish_text"

    def run(self, text: str) -> str:
        return materialtext.convert(text, ADMONISH_CONVERTERS)


class MdbookRenderer(github.GithubRenderer):
    """Renders Markdown for mdBook (GitHub flavour, optionally `mdbook-admonish`)."""

    name = "mdbook"

    def __init__(self, *, admonish: bool = False) -> None:
        """Constructor.

        Args:
            admonish: Render admonitions for the `mdbook-admonish` preprocessor
                      (default: GitHub alerts / `<details>`, which mdBook renders natively)
        """
        self.admonish = admonish

    def __repr__(self) -> str:
        return f"{type(self).__name__}(admonish={self.admonish})"

    def processors(self, node: mknode.MkNode) -> list[TextProcessor]:
        result = super().processors(node)
        if not self.admonish:
            return result
        return [
            AdmonishTextProcessor() if isinstance(p, github.MaterialTextProcessor) else p
            for p in result
        ]


def _uses_admonish(r: base.Renderer) -> bool:
    return isinstance(r, MdbookRenderer) and r.admonish


@MdbookRenderer.rule(mk.MkAdmonition)
def render_admonition(node: mk.MkAdmonition, r: base.Renderer) -> str:
    if not _uses_admonish(r):
        return github.render_admonition(node, r)
    if not node.title and not node.get_items():
        return ""
    text = r.render_children(node.get_items())
    if node.annotations:
        text = f"{text}\n\n{r.render_markdown(node.annotations)}"
    return admonish(node.typ, text, node.title, collapsible=node.collapsible)


@MdbookRenderer.rule(mk.MkCompactAdmonition)
def render_compact_admonition(node: mk.MkCompactAdmonition, r: base.Renderer) -> str:
    if not _uses_admonish(r):
        return github.render_compact_admonition(node, r)
    text = node.get_text()
    if isinstance(text, mk.MkNode):
        text = (r.render_child(text)).markdown
    return admonish(node.typ or "note", text)


@MdbookRenderer.rule(mk.MkDetailsBlock)
def render_details_block(node: mk.MkDetailsBlock, r: base.Renderer) -> str:
    if not _uses_admonish(r):
        return github.render_details_block(node, r)
    text = r.render_children(node.get_items())
    title = node.title or node.typ.capitalize()
    return admonish(node.typ, text, title, collapsible=True)

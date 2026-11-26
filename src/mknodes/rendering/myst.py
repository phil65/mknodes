"""MyST flavour: Markdown for Sphinx with `myst-parser` and `sphinx-design`.

Based on the GitHub flavour (MyST is CommonMark; raw HTML, badges, icons and Griffe API
docs stay the same), but with MyST directives in colon fences (the `colon_fence`
extension):

- admonitions: `:::{note}`, with a title `:::{admonition} Title` + `:class: note`
- collapsible admonitions / details: `:::{dropdown} Title` (sphinx-design)
- tabs: `::::{tab-set}` with `:::{tab-item} Title` (sphinx-design)
- code blocks with title / line numbers / highlighted lines: `{code-block}` with
  `:caption:`, `:linenos:`, `:lineno-start:`, `:emphasize-lines:`

Hand-written Material blocks (`!!!`, `???`, `===`, `/// details`, `::: path`, code fence
options) in page text get converted to the same directives.
"""

import dataclasses
import re
from typing import TYPE_CHECKING

import mknodes as mk
from mknodes.rendering import github, materialtext


if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    from mknodes.basenodes.processors import TextProcessor
    from mknodes.build.output import BuildOutput
    from mknodes.rendering import base
    from mknodes.utils import resources


# Material admonition type -> docutils admonition (the ones Sphinx themes style).
ADMONITION_TYPES = {
    "note": "note",
    "abstract": "note",
    "info": "note",
    "example": "note",
    "quote": "note",
    "tip": "tip",
    "success": "tip",
    "hint": "hint",
    "question": "hint",
    "important": "important",
    "attention": "attention",
    "caution": "caution",
    "warning": "warning",
    "failure": "error",
    "error": "error",
    "danger": "danger",
    "bug": "error",
    "seealso": "seealso",
}
# Admonition type -> sphinx-design color of a dropdown.
DROPDOWN_COLORS = {
    "note": "info",
    "hint": "info",
    "seealso": "info",
    "tip": "success",
    "important": "primary",
    "attention": "warning",
    "caution": "warning",
    "warning": "warning",
    "error": "danger",
    "danger": "danger",
}
COLON_FENCE_RE = re.compile(r"^[ \t]*(:{3,})", re.MULTILINE)
BACKTICK_FENCE_RE = re.compile(r"^[ \t]*(`{3,})", re.MULTILINE)
MYST_DIRECTIVE_RE = re.compile(r"^\s*\{[\w-]+\}")
# A line starting with an API docs anchor: a heading or the anchor alone.
TARGET_LINE_RE = re.compile(r'^(?P<indent>[ \t]*)(?:#{1,6} +)?<a id="(?P<id>[A-Za-z_][\w.]*)"></a>')


def directive_fence(text: str, *, backticks: bool = False) -> str:
    """Return a fence longer than any fence of the same kind in given text (nesting)."""
    pattern, char = (BACKTICK_FENCE_RE, "`") if backticks else (COLON_FENCE_RE, ":")
    inner = max((len(m) for m in pattern.findall(text)), default=0)
    return char * max(3, inner + 1)


def directive(
    name: str,
    text: str,
    argument: str | None = None,
    options: dict[str, str | None] | None = None,
    *,
    backticks: bool = False,
) -> str:
    """Return a MyST directive in a colon fence (`:::{name} argument`).

    Directives converted from page text use backtick fences instead: page text gets
    converted after its nodes rendered, so it may sit inside a colon-fenced directive
    whose fence length did not account for it.
    """
    fence = directive_fence(text, backticks=backticks)
    head = f"{fence}{{{name}}} {argument}" if argument else f"{fence}{{{name}}}"
    lines = [head]
    for key, value in (options or {}).items():
        lines.append(f":{key}: {value}" if value else f":{key}:")
    return "\n".join(lines) + f"\n\n{text.strip()}\n\n{fence}\n"


def admonition(typ: str, text: str, title: str | None = None, *, backticks: bool = False) -> str:
    """Return an admonition (`:::{note}`, with title: `:::{admonition} Title`)."""
    kind = ADMONITION_TYPES.get(typ, "note")
    if title:
        return directive("admonition", text, title, {"class": kind}, backticks=backticks)
    return directive(kind, text, backticks=backticks)


def dropdown(
    title: str,
    text: str,
    typ: str | None = None,
    *,
    open_: bool = False,
    backticks: bool = False,
) -> str:
    """Return a collapsible block (`:::{dropdown}` of sphinx-design)."""
    options: dict[str, str | None] = {}
    if open_:
        options["open"] = None
    if typ and (color := DROPDOWN_COLORS.get(ADMONITION_TYPES.get(typ, ""))):
        options["color"] = color
    return directive("dropdown", text, title, options, backticks=backticks)


def tab_set(tabs: list[tuple[str, str]], selected: int = 0, *, backticks: bool = False) -> str:
    """Return a `::::{tab-set}` of `:::{tab-item}`s ((title, text) pairs).

    Empty tabs get left out (a `tab-item` needs content).
    """
    items = [
        directive(
            "tab-item",
            text,
            title,
            {"selected": None} if i == selected else None,
            backticks=backticks,
        )
        for i, (title, text) in enumerate(tabs)
        if text.strip()
    ]
    return directive("tab-set", "\n".join(items), backticks=backticks) if items else ""


def code_block(
    code: str,
    language: str = "",
    *,
    fence: str = "```",
    caption: str | None = None,
    linenos: int | None = None,
    emphasize_lines: list[int] | None = None,
) -> str:
    """Return a code block, a `{code-block}` directive if it has options."""
    options = _code_options(caption, linenos, emphasize_lines)
    if not options:
        return f"{fence}{language}\n{code}\n{fence}"
    head = f"{fence}{{code-block}} {language}".rstrip()
    return "\n".join([head, *options, code, fence])


def _code_options(
    caption: str | None, linenos: int | None, emphasize_lines: list[int] | None
) -> list[str]:
    options = []
    if caption:
        options.append(f":caption: {caption}")
    if linenos is not None:
        options.append(":linenos:")
        if linenos != 1:
            options.append(f":lineno-start: {linenos}")
    if emphasize_lines:
        options.append(f":emphasize-lines: {','.join(str(i) for i in emphasize_lines)}")
    return options


def _hl_lines(value: str) -> list[int]:
    """Parse Material's `hl_lines="1 3-4"` into line numbers."""
    lines: list[int] = []
    for part in value.split():
        start, _, end = part.partition("-")
        if start.isdigit() and (not end or end.isdigit()):
            lines.extend(range(int(start), int(end or start) + 1))
    return lines


def _material_fence(fence: str, info: str) -> str:
    """Material fence options (`py title="x" linenums="1" hl_lines="2"`) -> `{code-block}`."""
    if MYST_DIRECTIVE_RE.match(info) or ("=" not in info and not info.strip().startswith("{")):
        return f"{fence}{info}"  # a MyST directive (`{code-block}`) or no Material options
    lang, opts = materialtext.parse_fence_info(info)
    linenums = opts.get("linenums")
    options = _code_options(
        opts.get("title"),
        int(linenums) if linenums and linenums.isdigit() else None,
        _hl_lines(opts.get("hl_lines", "")),
    )
    if not options:
        return f"{fence}{lang}"
    return "\n".join([f"{fence}{{code-block}} {lang}".rstrip(), *options])


def _material_admonition(adm: materialtext.Admonition) -> str:
    if adm.collapsible:
        title = adm.title or adm.typ.capitalize()
        return dropdown(title, adm.text, adm.typ, open_=adm.expanded, backticks=True)
    return admonition(adm.typ, adm.text, adm.title, backticks=True)


def _material_tabs(tabs: list[materialtext.Tab]) -> str:
    selected = next((i for i, tab in enumerate(tabs) if tab.selected), 0)
    return tab_set([(tab.title, tab.text) for tab in tabs], selected, backticks=True)


def _material_block(block: materialtext.Block) -> str:
    if block.name in {"details", "tab"}:
        return dropdown(block.argument or block.name.capitalize(), block.text, backticks=True)
    if block.name == "admonition" or block.name in ADMONITION_TYPES:
        typ = "note" if block.name == "admonition" else block.name
        return admonition(typ, block.text, block.argument, backticks=True)
    return block.text


MYST_CONVERTERS = dataclasses.replace(
    github.MATERIAL_CONVERTERS,
    admonition=_material_admonition,
    tabs=_material_tabs,
    fence_info=_material_fence,
    block=_material_block,
)


class MystTextProcessor(github.MaterialTextProcessor):
    """Convert hand-written Material blocks of a page into MyST directives."""

    ID = "myst_text"

    def run(self, text: str) -> str:
        return materialtext.convert(text, MYST_CONVERTERS)


class MystRenderer(github.GithubRenderer):
    """Renders MyST Markdown for Sphinx (`myst-parser` + `sphinx-design`)."""

    name = "myst"

    def to_html(self, markdown: str, reqs: resources.Resources | None = None) -> str:
        from mknodes.rendering import html as html_render

        return html_render.myst(markdown, reqs)

    def processors(self, node: mknode.MkNode) -> list[TextProcessor]:
        return [
            MystTextProcessor() if isinstance(p, github.MaterialTextProcessor) else p
            for p in super().processors(node)
        ]

    def finalize(self, output: BuildOutput, root: mk.MkNav) -> None:
        """Link `[title][dotted.path]` references, add MyST targets for the anchors."""
        super().finalize(output, root)
        add_targets(output)


@MystRenderer.rule(mk.MkAdmonition)
async def render_admonition(node: mk.MkAdmonition, r: base.Renderer) -> str:
    if not node.title and not node.get_items():
        return ""
    text = await r.render_children(node.get_items())
    if node.annotations:
        text = f"{text}\n\n{await r.render_markdown(node.annotations)}"
    if node.collapsible:
        title = node.title or node.typ.capitalize()
        return dropdown(title, text, node.typ, open_=bool(node.expanded))
    return admonition(node.typ, text, node.title)


@MystRenderer.rule(mk.MkCompactAdmonition)
async def render_compact_admonition(node: mk.MkCompactAdmonition, r: base.Renderer) -> str:
    text = await node.get_text()
    if isinstance(text, mk.MkNode):
        text = (await r.render_child(text)).markdown
    return admonition(node.typ or "note", text)


@MystRenderer.rule(mk.MkDetailsBlock)
async def render_details_block(node: mk.MkDetailsBlock, r: base.Renderer) -> str:
    text = await r.render_children(node.get_items())
    title = node.title or node.typ.capitalize()
    return dropdown(title, text, node.typ, open_=bool(node.expanded))


@MystRenderer.rule(mk.MkTab, mk.MkTabBlock)
async def render_tab(node: mk.MkTab | mk.MkTabBlock, r: base.Renderer) -> str:
    """A single tab outside a tab container: a dropdown."""
    text = await r.render_children(node.get_items())
    return dropdown(node.title, text, open_=bool(node.select))


@MystRenderer.rule(mk.MkTabContainer)
async def render_tab_container(node: mk.MkTabContainer, r: base.Renderer) -> str:
    """A sphinx-design tab set, the selected (or first) tab selected."""
    tabs = node.get_items()
    if not tabs:
        return ""
    selected = node.select_tab if node.select_tab is not None else 0
    if isinstance(selected, str):
        selected = node._get_tab_pos(selected)
    items = [(tab.title, await r.render_children(tab.get_items())) for tab in tabs]
    return tab_set(items, selected)


@MystRenderer.rule(mk.MkCode)
async def render_code(node: mk.MkCode, r: base.Renderer) -> str:
    """Code block, a `{code-block}` directive for title / line numbers / highlights."""
    text = await node.get_text()
    return code_block(
        text,
        node.language or "",
        fence=node.fence_for(text),
        caption=node.title or None,
        linenos=node.linenums,
        emphasize_lines=node.highlight_lines,
    )


def add_targets(output: BuildOutput) -> None:
    """Give the API docs anchors (`<a id="pkg.Klass">`) MyST targets, in place.

    MyST checks `[title](page.md#id)` links against the headings and targets of the
    page, not against raw HTML ids. The anchor an object's references link to gets a
    `(pkg.Klass)=` target (Sphinx labels are global and lowercase: one per name), the
    links to it the lowercase name.
    """
    from mknodes.build import refcheck

    names: dict[str, str] = {}  # lowercase name -> anchor id
    by_page: dict[str, set[str]] = {}
    for page, anchor in sorted(set(refcheck.find_anchors(output).values())):
        if anchor.lower() in names:
            continue
        names[anchor.lower()] = anchor
        by_page.setdefault(page, set()).add(anchor)
    added: set[str] = set()
    for page, anchors in by_page.items():
        lines = output.pages[page].split("\n")
        for lineno, line in reversed(list(refcheck.iter_markdown_lines(output.pages[page]))):
            match = TARGET_LINE_RE.match(line)
            if not match or match["id"] not in anchors or match["id"] in added:
                continue
            added.add(match["id"])
            lines.insert(lineno - 1, f"{match['indent']}({match['id']})=")
        output.pages[page] = "\n".join(lines)
    ids = {anchor for anchor in added if anchor != anchor.lower()}
    if not ids:
        return
    pattern = re.compile(r"#(" + "|".join(map(re.escape, sorted(ids))) + r")\)")
    for page, markdown in output.pages.items():
        output.pages[page] = pattern.sub(lambda m: f"#{m[1].lower()})", markdown)

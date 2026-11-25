"""Manual page "Markdown flavours": the same nodes rendered as Material and GitHub Markdown.

Everything shown on the page is generated from the renderers, so it stays correct
when rules get added or changed.
"""

from __future__ import annotations

import inspect
import re
from typing import TYPE_CHECKING, Any

import mknodes as mk
from mknodes import rendering
from mknodes.info import nodefile
from mknodes.utils import resources


if TYPE_CHECKING:
    from collections.abc import Collection


INTRO = """\
Nodes render to the Markdown of a *flavour*. The default flavour, `material`, is
Markdown for [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) /
Zensical, using Python-Markdown / PyMdown extensions (admonitions, tabs, attribute
lists, ...). The `github` flavour produces GitHub flavoured Markdown for READMEs, issues
and wikis: alerts, `<details>` blocks, `<kbd>` and plain fenced code.

```py
import mknodes as mk

node = mk.MkAdmonition("Careful!", typ="warning")
await node.to_markdown()  # Material (default)
await node.to_markdown(flavor="github")  # > [!WARNING] ...
```

A whole site can be generated in a flavour with the CLI. The `markdown` engine writes
plain Markdown files plus a `SUMMARY.md` nav and defaults to `github`:

```bash
mknodes generate --engine markdown --flavor github --generated-dir build/markdown
```

The flavour can also be set with the `flavor` setting (see
[Configuration](<../Site generator/configuration.md>)) or passed to
[DocBuilder][mknodes.DocBuilder]. The renderer classes are documented in
[Core API / Rendering](<../Core API/rendering.md>).
"""

COMPARISON_INTRO = """\
Each node is shown as rendered on this site, followed by its Markdown in both flavours.
"""

RULES_INTRO = """\
How the `github` flavour renders each node. A node either has a *rule* (a render
function registered with `GithubRenderer.rule`, also used for subclasses which don't
render themselves), an `[output.github]` *template* in its node file, or renders its
*default* Markdown, the same as in the `material` flavour. That is fine for plain
Markdown (text, tables, lists); output that needs Markdown extensions (last column) may
not display on GitHub. Containers rendering their default Markdown still render their
children in the GitHub flavour, and hand-written Material admonitions / tabs in page text
get converted.
"""


def _examples() -> dict[str, mk.MkNode]:
    return {
        "Admonition": mk.MkAdmonition("Content with **Markdown**.", typ="warning", title="Careful"),
        "Collapsible admonition": mk.MkAdmonition(
            "Hidden until clicked.", typ="info", title="Click me", collapsible=True
        ),
        "Tabs": mk.MkTabbed({
            "Python": mk.MkCode("import mknodes as mk", language="py"),
            "Shell": mk.MkCode("pip install mknodes", language="bash"),
        }),
        "Code block with title": mk.MkCode(
            "import mknodes as mk\n\nnav = mk.MkNav()", language="py", title="build.py"
        ),
        "Keys": mk.MkKeys("Ctrl+Alt+Del"),
        "Details block": mk.MkDetailsBlock("Some details.", title="More info", typ="tip"),
        "Definition list": mk.MkDefinitionList({
            "MkNav": "A section of the documentation.",
            "MkPage": "A page of the documentation.",
        }),
        "Critic markup": mk.MkCritic("Inserted text", typ="addition"),
        "Progress bar": mk.MkProgressBar(60),
        "Icon": mk.MkIcon("mdi:github", height=24),
        "Link with icon": mk.MkLink(
            "https://github.com/phil65/mknodes", "Repository", icon="mdi:github"
        ),
        "Material badge": mk.MkMaterialBadge("mdi:tag", "4.1.0"),
        "Docstrings": mk.MkDocStrings(
            "mknodes.rendering.github.alert", show_root_heading=True, heading_level=4
        ),
    }


def _longest_backtick_run(text: str) -> int:
    return max((len(m) for m in re.findall(r"`+", text)), default=0)


class FlavorComparison(mk.MkNode):
    """Markdown of a node in the Material and the GitHub flavour, side by side."""

    REQUIRED_EXTENSIONS = [resources.Extension("md_in_html")]

    def __init__(self, node: mk.MkNode, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.node = node

    async def to_md_unprocessed(self) -> str:
        outputs = {
            "Material": await self.node.to_markdown(flavor="material"),
            "GitHub": await self.node.to_markdown(flavor="github"),
        }
        fence_level = max(0, *(_longest_backtick_run(v) - 2 for v in outputs.values()))
        # The code blocks render in the active flavour (the page's).
        blocks = [
            await mk.MkCode(
                text.strip(), language="markdown", title=title, fence_level=fence_level
            ).to_markdown()
            for title, text in outputs.items()
        ]
        content = "\n\n".join(blocks)
        if rendering.current().name != "material":
            return content
        return f'<div class="grid" markdown>\n\n{content}\n\n</div>\n'


def _github_support(klass: type[mk.MkNode]) -> tuple[str, str]:
    """Return how the GitHub renderer renders given class and the rule's summary."""
    renderer = rendering.get_renderer_class("github")
    rule = renderer.find_rule(klass)
    if rule is None:
        return "Default", ""
    for base in klass.__mro__:
        via = "" if base is klass else f" of `{base.__name__}`"
        for renderer_cls in renderer.__mro__:
            if getattr(renderer_cls, "_rules", {}).get(base) is rule:
                doc = inspect.getdoc(rule) or ""
                return f"Rule{via}", doc.splitlines()[0] if doc else ""
        file = nodefile.get_nodefile(base) if base.__module__.startswith("mknodes") else None
        if file and renderer.template_key in file.output:
            return f"Template{via}", f"`[output.{renderer.template_key}]` in the node file"
    return "Rule", ""


def _node_classes() -> list[type[mk.MkNode]]:
    classes = {
        obj
        for name in mk.__all__
        if isinstance(obj := getattr(mk, name), type)
        and issubclass(obj, mk.MkNode)
        and not issubclass(obj, mk.MkPage | mk.MkNav)
        and obj is not mk.MkNode
    }
    return sorted(classes, key=lambda c: c.__name__)


def rules_table(documented: Collection[type]) -> mk.MkTable:
    """Table of all node classes and how the GitHub flavour renders them.

    Args:
        documented: Classes having a node page (get linked).
    """
    columns = ["Node", "GitHub output", "Details", "Extensions of the Material output"]
    table = mk.MkTable(columns=columns)
    for klass in _node_classes():
        name = klass.__name__
        link = f"[{name}][mknodes.{name}]" if klass in documented else f"`{name}`"
        kind, details = _github_support(klass)
        extensions = ", ".join(f"`{ext}`" for ext in klass.REQUIRED_EXTENSIONS)
        table.add_row((link, kind, details, extensions))
    return table


def build_page(page: mk.MkPage, documented: Collection[type]) -> None:
    """Populate the flavours page.

    Args:
        page: The page to populate.
        documented: Node classes having a node page (get linked).
    """
    page += INTRO
    page += mk.MkHeader("Side by side", level=2)
    page += COMPARISON_INTRO
    for title, node in _examples().items():
        page += mk.MkHeader(title, level=3)
        page += node
        page += FlavorComparison(node)
    page += mk.MkHeader("GitHub rules", level=2)
    page += RULES_INTRO
    page += rules_table(documented)

"""Manual section "Core API": docstrings of the classes used to build a site.

Node classes are documented on their own pages ("The nodes"), the site generator
settings on "Site generator -> Configuration". This section covers the rest of the
public API users work with directly.
"""

from typing import Any

import mknodes as mk


nav = mk.MkNav("Core API")

DOCSTRING_OPTIONS: dict[str, Any] = dict(
    show_root_heading=True,
    show_root_full_path=True,
    heading_level=2,
    show_source=False,
)

PAGES: dict[str, list[str]] = {
    "Navs and pages": ["mknodes.MkNav", "mknodes.MkPage"],
    "Routing": ["mknodes.Router", "mknodes.navs.navrouter.NavRouter"],
    "MkNode": ["mknodes.MkNode"],
    "Theming": ["mknodes.Theme", "mknodes.MaterialTheme"],
    "Build step": [
        "mknodes.DocBuilder",
        "mknodes.BuildOutput",
        "mknodes.build.output.NavItem",
        "mknodes.MarkdownExporter",
    ],
    "Rendering": [
        "mknodes.rendering.get_renderer",
        "mknodes.rendering.use",
        "mknodes.rendering.Renderer",
        "mknodes.rendering.MaterialRenderer",
        "mknodes.rendering.github.GithubRenderer",
        "mknodes.rendering.myst.MystRenderer",
    ],
}

INDEX_TEXT = """\
The classes you build a documentation with. Nodes (the Markdown fragments, from
[MkText][mknodes.MkText] to [MkDocStrings][mknodes.MkDocStrings]) are documented on
their own pages in [The nodes](<../The nodes/index.md>), each with live examples. The
settings of the site generator (`[tool.mknodes]` / the `mknodes` plugin entry) are
listed on [Site generator / Configuration](<../Site generator/configuration.md>).
"""

INTROS: dict[str, str] = {
    "Navs and pages": """\
A documentation is a tree: [MkNav][mknodes.MkNav] objects are the sections,
[MkPage][mknodes.MkPage] objects the pages, nodes the content of a page. Nodes get added
with `+=`, navs and pages with `add_nav()` / `add_page()` (or via decorators, see
[Routing](routing.md)). The root nav is what a build function receives.
""",
    "Routing": """\
Instead of adding pages imperatively, functions can get registered for a nav path.
`nav.route` is a [NavRouter][mknodes.navs.navrouter.NavRouter] bound to the nav,
[Router][mknodes.Router] collects routes without a nav (for example in a module which
gets imported by several build functions) and attaches them via `register_nodes(nav)`.
The [MkNavs / Using decorators](<../MkNavs/Using decorators/index.md>) section is built this way.
""",
    "MkNode": """\
The base class of every node, page and nav: tree handling (`parent`, `children`,
`iter_nodes()`), the project context (`ctx`), the Jinja environment (`env`) and the
rendering API (`node.to_markdown_sync()` / `str(node)`, `to_html_sync()`,
`get_resources_sync()`). Rendering is synchronous and never fetches: external inputs
(icons, remote files, LLM texts, ...) come from the inputs store, resolved before rendering
(the async `to_markdown()` / `to_html()` / `get_resources()` are deprecated wrappers, removed
in 5.0). `to_html_sync(flavor=...)` converts with a parser that knows the flavour:
Python-Markdown for `material`, comrak for `github` / `mdbook`, markdown-it-py with the MyST
plugins (directives mapped to Sphinx-like HTML, an approximation) for `myst`; the last two
need the `html` extra (`pip install mknodes[html]`). Its node page
([MkNode](<../The nodes/Base nodes/mknode.md>)) shows the examples.
""",
    "Theming": """\
A build function receives the theme next to the root nav. [Theme][mknodes.Theme] holds
the template overrides, CSS and the error page, [MaterialTheme][mknodes.MaterialTheme]
adds Material for MkDocs settings (palette, colors, content width, status icons).
""",
    "Build step": """\
[DocBuilder][mknodes.DocBuilder] renders a node tree into a
[BuildOutput][mknodes.BuildOutput]: pages (Markdown of one flavour), assets, the nav as
[NavItem][mknodes.build.output.NavItem] tree and the Markdown extensions / CSS / JS the
pages need. [MarkdownExporter][mknodes.MarkdownExporter] writes it as plain Markdown
files plus a `SUMMARY.md` nav. The site generator (`mknodes build`) does the same and
then runs Zensical, so this is only needed to use MkNodes without it.
""",
    "Rendering": """\
Renderers turn nodes into the Markdown of a flavour (`material`, the default, or
`github`). See [Markdown flavours](<../The nodes/markdown_flavours.md>) for what changes
between them.
""",
}

EXAMPLES: dict[str, str] = {
    "Navs and pages": """\
import mknodes as mk

nav = mk.MkNav()  # the root nav
page = nav.add_page("Usage", is_index=True, hide="toc")
page += mk.MkAdmonition("Install with `pip install mknodes`.", typ="tip")
guides = nav.add_nav("Guides")
first_steps = guides.add_page("First steps")
first_steps += "Some text"
""",
    "Routing": """\
import mknodes as mk

nav = mk.MkNav("Guides")


@nav.route.page("First steps", icon="rocket")
def _(page: mk.MkPage):
    page += "Some text"


@nav.route.nav("Advanced")
def _(nav: mk.MkNav):
    nav.add_page("Plugins")
""",
    "MkNode": """\
import mknodes as mk

node = mk.MkAdmonition("Careful!", typ="warning")
markdown = node.to_markdown_sync()  # same as str(node)
html = node.to_html_sync()
github_html = node.to_html_sync(flavor="github")  # needs mknodes[html]
resources = node.get_resources_sync()  # Markdown extensions, CSS, JS
""",
    "Theming": """\
import mknodes as mk


def build(root: mk.MkNav, theme: mk.Theme) -> mk.MkNav:
    theme.error_page.content = mk.MkAdmonition("Page does not exist!")
    if isinstance(theme, mk.MaterialTheme):
        theme.content_area_width = 1300
    page = root.add_page("Home", is_index=True)
    page += "Hello"
    return root
""",
    "Build step": """\
import mknodes as mk

nav = mk.MkNav()
page = nav.add_page("Usage", is_index=True)
page += mk.MkAdmonition("Install with `pip install mknodes`.", typ="tip")

output = mk.DocBuilder(flavor="github").build_sync(nav)
mk.MarkdownExporter().export_sync(output, "site/")  # index.md + SUMMARY.md
""",
    "Rendering": """\
import mknodes as mk
from mknodes import rendering

node = mk.MkAdmonition("Careful!", typ="warning")
node.to_markdown_sync(flavor="github")  # > [!WARNING] ...

with rendering.use(rendering.get_renderer("github")):
    str(node)  # nested nodes, templates and str() render in that flavour
""",
}


def _add_page(title: str, identifiers: list[str]) -> None:
    @nav.route.page(title, hide="toc")
    def _(page: mk.MkPage) -> None:
        page += INTROS[title]
        page += mk.MkCode(EXAMPLES[title].rstrip(), language="py", title="Example")
        for identifier in identifiers:
            page += mk.MkDocStrings(identifier, **DOCSTRING_OPTIONS)


@nav.route.page(is_index=True, hide="toc", icon="api")
def _(page: mk.MkPage) -> None:
    page += INDEX_TEXT
    table = mk.MkTable(columns=["Page", "Objects"])
    for title, identifiers in PAGES.items():
        filename = f"{title.lower().replace(' ', '_')}.md"
        objects = ", ".join(f"[`{i.rsplit('.', 1)[-1]}`][{i}]" for i in identifiers)
        table.add_row((f"[{title}]({filename})", objects))
    page += table


for _title, _identifiers in PAGES.items():
    _add_page(_title, _identifiers)

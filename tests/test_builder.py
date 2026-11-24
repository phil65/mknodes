from __future__ import annotations

from typing import TYPE_CHECKING

import mknodes as mk
from mknodes.build import DocBuilder, MarkdownExporter, NavItem
from mknodes.utils import resources


if TYPE_CHECKING:
    import pathlib


class ScriptNode(mk.MkText):
    """Node requiring an inline script, a linked script and inline CSS."""

    JS_FILES = [
        resources.JSText("console.log(1)", "inline.js"),
        resources.JSFile("https://cdn.example.org/lib.js"),
    ]
    CSS = [resources.CSSText("p {color: red}", "style.css")]


JS_PATH = f"assets/{ScriptNode.JS_FILES[0].resolved_filename}"  # content-hashed name
CSS_PATH = f"assets/{ScriptNode.CSS[0].resolved_filename}"


def build_tree() -> mk.MkNav:
    root = mk.MkNav()
    index = root.add_page("Intro", is_index=True)
    index += ScriptNode("intro")
    section = root.add_nav("Section")
    page = section.add_page("Details")
    page += mk.MkAdmonition("careful", typ="warning")
    page.template.announcement_bar = "Hello"
    return root


async def test_build_output():
    output = await DocBuilder().build(build_tree())
    assert set(output.pages) == {"index.md", "Section/details.md"}
    assert output.flavor == "material"
    assert "!!! warning" in output.pages["Section/details.md"]
    assert output.nav == [
        NavItem("Intro", "index.md"),
        NavItem("Section", children=[NavItem("Details", "Section/details.md")]),
    ]
    assert "admonition" in output.markdown_extensions
    # resources became assets / scripts / stylesheets
    assert output.assets[JS_PATH] == "console.log(1)"
    assert [s.path for s in output.extra_javascript] == [
        "https://cdn.example.org/lib.js",
        JS_PATH,
    ]
    assert CSS_PATH in output.extra_css
    assert "p {color: red}" in str(output.assets[CSS_PATH])
    # page template override got rendered and referenced
    assert "Section/details.html" in output.templates
    assert "Hello" in output.templates["Section/details.html"]
    assert "template: Section/details.html" in output.pages["Section/details.md"]
    assert "admonition" in output.page_resources["Section/details.md"].markdown_extensions


async def test_build_output_github_flavor():
    output = await DocBuilder(flavor="github").build(build_tree())
    assert output.flavor == "github"
    assert output.pages["Section/details.md"].startswith("# Details\n\n> [!WARNING]")


async def test_non_global_resources_go_into_page_template():
    output = await DocBuilder(global_resources=False).build(build_tree())
    assert output.extra_javascript == []
    assert JS_PATH in output.assets
    assert JS_PATH in output.templates["index.html"]


async def test_parallel_rendering_gives_same_pages():
    sequential = await DocBuilder(flavor="github").build(build_tree())
    parallel = await DocBuilder(flavor="github", max_workers=4).build(build_tree())
    assert parallel.pages == sequential.pages


async def test_markdown_exporter(tmp_path: pathlib.Path):
    output = await DocBuilder(flavor="github").build(build_tree())
    await MarkdownExporter().export(output, tmp_path)
    assert (tmp_path / "Section" / "details.md").read_text().startswith("# Details")
    assert (tmp_path / JS_PATH).is_file()
    summary = (tmp_path / "SUMMARY.md").read_text()
    assert "- [Intro](index.md)\n- Section\n    - [Details](Section/details.md)" in summary


def test_route_registration_order_is_declaration_order():
    nav = mk.MkNav("Section")
    titles = [f"Page {i}" for i in range(12)]
    for title in titles:

        @nav.route.page(title)
        def _(page: mk.MkPage, title=title):
            import time

            time.sleep(0.001 * (12 - len(title)))  # later pages finish first
            page += title

    assert [p.title for p in nav.nav.get_pages()] == titles

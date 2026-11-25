"""Regressions found by building a GitHub profile README with mknodes."""

from __future__ import annotations

import markdown
import pytest

import mknodes as mk


FLAVORS = ["material", "github"]


@pytest.mark.parametrize("flavor", FLAVORS)
async def test_html_block_keeps_wrapper_element(flavor: str):
    block = mk.MkHtmlBlock('<img src="a.png">', block_type="picture", attributes={"id": "x"})
    md = await block.to_markdown(flavor=flavor)
    if flavor == "material":
        assert md == '/// html | picture\n    id: x\n\n<img src="a.png">\n///\n'
    else:
        assert md == '<picture id="x">\n<img src="a.png">\n</picture>'


async def test_html_block_markdown_content_github():
    assert await mk.MkHtmlBlock("**b**").to_markdown(flavor="github") == "<div>\n\n**b**\n\n</div>"
    span = mk.MkHtmlBlock("x", block_type="span", attributes={"title": 'a"b'})
    assert await span.to_markdown(flavor="github") == '<span title="a&quot;b">x</span>'


@pytest.mark.parametrize("flavor", FLAVORS)
async def test_link_to_url_without_project(flavor: str, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no pyproject.toml here or above
    link = mk.MkLink("https://example.org", "x")
    assert await link.to_markdown(flavor=flavor) == "[x](https://example.org)"


def test_fallback_context_without_pyproject(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from mknodes.info import contexts

    assert contexts.ProjectContext().metadata.pyproject_file.name is None


@pytest.mark.parametrize("flavor", FLAVORS)
async def test_table_escapes_pipes(flavor: str):
    table = mk.MkTable([["a|b", "`x|y`"]], columns=["A|", "B"])
    md = await table.to_markdown(flavor=flavor)
    if flavor == "material":  # Python-Markdown keeps pipes in code spans
        assert md == "| A\\|  | B     |\n| ---- | ----- |\n| a\\|b | `x|y` |\n"
        html = markdown.markdown(md, extensions=["tables"])
        assert "<td>a|b</td>" in html
        assert "<td><code>x|y</code></td>" in html
    else:  # GFM needs them escaped everywhere
        assert md == "| A\\|  | B      |\n| ---- | ------ |\n| a\\|b | `x\\|y` |\n"


@pytest.mark.parametrize("flavor", FLAVORS)
async def test_table_list_of_lists_are_rows(flavor: str):
    table = mk.MkTable([["1", "2"], ["3", None]], columns=["A", "B"])
    assert [str(cell) for cell in table.data["A"]] == ["1", "3"]
    md = await table.to_markdown(flavor=flavor)
    assert md == "| A | B |\n| - | - |\n| 1 | 2 |\n| 3 |   |\n"
    # Without columns, the first row is the header.
    headed = mk.MkTable([["A", "B"], ["1", 2]])
    assert headed.columns == ["A", "B"]
    assert await headed.to_markdown(flavor=flavor) == "| A | B |\n| - | - |\n| 1 | 2 |\n"

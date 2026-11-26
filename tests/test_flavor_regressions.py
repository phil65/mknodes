"""Regressions found by building a GitHub profile README with mknodes."""

import inspect

import markdown
import pytest

import mknodes as mk
from mknodes.rendering import github


FLAVORS = ["material", "github"]


@pytest.mark.parametrize("flavor", FLAVORS)
def test_html_block_keeps_wrapper_element(flavor: str):
    block = mk.MkHtmlBlock('<img src="a.png">', block_type="picture", attributes={"id": "x"})
    md = block.to_markdown(flavor=flavor)
    if flavor == "material":
        assert md == '/// html | picture\n    id: x\n\n<img src="a.png">\n///\n'
    else:
        assert md == '<picture id="x">\n<img src="a.png">\n</picture>'


def test_html_block_markdown_content_github():
    assert mk.MkHtmlBlock("**b**").to_markdown(flavor="github") == "<div>\n\n**b**\n\n</div>"
    span = mk.MkHtmlBlock("x", block_type="span", attributes={"title": 'a"b'})
    assert span.to_markdown(flavor="github") == '<span title="a&quot;b">x</span>'


@pytest.mark.parametrize("flavor", FLAVORS)
def test_link_to_url_without_project(flavor: str, tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)  # no pyproject.toml here or above
    link = mk.MkLink("https://example.org", "x")
    assert link.to_markdown(flavor=flavor) == "[x](https://example.org)"


def test_fallback_context_without_pyproject(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    from mknodes.info import contexts

    assert contexts.ProjectContext().metadata.pyproject_file.name is None


@pytest.mark.parametrize("flavor", FLAVORS)
def test_table_escapes_pipes(flavor: str):
    table = mk.MkTable([["a|b", "`x|y`"]], columns=["A|", "B"])
    md = table.to_markdown(flavor=flavor)
    if flavor == "material":  # Python-Markdown keeps pipes in code spans
        assert md == "| A\\|  | B     |\n| ---- | ----- |\n| a\\|b | `x|y` |\n"
        html = markdown.markdown(md, extensions=["tables"])
        assert "<td>a|b</td>" in html
        assert "<td><code>x|y</code></td>" in html
    else:  # GFM needs them escaped everywhere
        assert md == "| A\\|  | B      |\n| ---- | ------ |\n| a\\|b | `x\\|y` |\n"


@pytest.mark.parametrize("flavor", FLAVORS)
def test_table_list_of_lists_are_rows(flavor: str):
    table = mk.MkTable([["1", "2"], ["3", None]], columns=["A", "B"])
    assert [str(cell) for cell in table.data["A"]] == ["1", "3"]
    md = table.to_markdown(flavor=flavor)
    assert md == "| A | B |\n| - | - |\n| 1 | 2 |\n| 3 |   |\n"
    # Without columns, the first row is the header.
    headed = mk.MkTable([["A", "B"], ["1", 2]])
    assert headed.columns == ["A", "B"]
    assert headed.to_markdown(flavor=flavor) == "| A | B |\n| - | - |\n| 1 | 2 |\n"


@pytest.mark.parametrize("flavor", FLAVORS)
def test_no_runs_of_blank_lines_around_details(flavor: str):
    page = mk.MkPage("P")
    page += "Intro"
    page += mk.MkAdmonition("body", collapsible=True, title="T")
    page += mk.MkAdmonition("alert body", typ="warning")
    page += "Outro"
    md = page.to_markdown(flavor=flavor)
    if flavor == "github":
        assert "\n\n\n" not in md
        assert "</details>\n\n> [!WARNING]" in md
    else:
        assert '??? info "T"\n    body' in md


def test_collapse_blank_lines_keeps_code_blocks():
    text = "a\n\n\n\nb\n```py\nx\n\n\n\ny\n```\n\n\nc ```inline``` d\n\n\ne"
    expected = "a\n\nb\n```py\nx\n\n\n\ny\n```\n\nc ```inline``` d\n\ne"
    assert github.collapse_blank_lines(text) == expected


def test_to_markdown_is_sync():
    assert not inspect.iscoroutinefunction(mk.MkNode.to_markdown)
    node = mk.MkAdmonition("x", typ="warning")
    assert node.to_markdown(flavor="github") == "> [!WARNING]\n> x\n"
    assert node.to_markdown() == "!!! warning\n    x\n"


async def test_to_markdown_inside_running_loop():
    node = mk.MkText("x")
    assert node.to_markdown(flavor="github") == node.to_markdown(flavor="github")


def test_html_table_markdown_cells_github():
    table = mk.MkHtmlTable({"A": [mk.MkAdmonition("x > y")], "B": [mk.MkCode("a<b")]})
    md = table.to_markdown(flavor="github")
    assert md.startswith("<table>\n<tr><th>A</th><th>B</th></tr>\n<tr>\n")
    assert "<td>\n\n> [!NOTE]\n> x > y\n\n</td>" in md
    assert "<td>\n\n```python\na<b\n```\n\n</td>" in md
    assert "&gt;" not in md
    assert "&lt;" not in md


def test_speech_bubble_markdown_content_github():
    bubble = mk.MkSpeechBubble("**b**", arrow="left")
    md = bubble.to_markdown(flavor="github")
    assert md == '<div class="speech left">\n\n**b**\n\n</div>'


@pytest.mark.parametrize("flavor", FLAVORS)
def test_commented_code_blank_line_after_html(flavor: str):
    node = mk.MkCommentedCode("# comment\nx = 1\n# another\ny = 2")
    md = node.to_markdown(flavor=flavor)
    assert "</div>\n\n```" in md
    assert "```\n\n<div" in md


def test_badge_is_shields_image_github():
    badge = mk.MkBadge("Doc-s", "my_site", badge_color="#ff9800", target="https://example.org")
    md = badge.to_markdown(flavor="github")
    url = "https://img.shields.io/badge/Doc--s-my__site-ff9800"
    assert md == f"[![Doc-s: my_site]({url})](https://example.org)"
    assert "<svg" in badge.to_markdown()


def test_nested_admonitions_github():
    inner = mk.MkAdmonition("x", typ="tip")
    outer = mk.MkAdmonition(mk.MkAdmonition(inner, typ="warning", title="W"), typ="note")
    md = outer.to_markdown(flavor="github")
    assert md == "> [!NOTE]\n> > **W**\n> >\n> > > **Tip**\n> > >\n> > > x\n"
    collapsible = mk.MkAdmonition(mk.MkAdmonition("y", typ="tip"), collapsible=True)
    assert "> [!TIP]\n> y" in collapsible.to_markdown(flavor="github")

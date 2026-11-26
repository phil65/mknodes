"""Flavour-aware `MkNode.to_html_sync()` (the "Html" tab of node examples)."""

import pytest

import mknodes as mk
from mknodes import rendering
from mknodes.rendering import html as html_render


RAW_MARKERS = ("[!", ":::", "!!!", "{warning}", "{note}", "{dropdown}", "{tab-")


def assert_rendered(html: str) -> None:
    for marker in RAW_MARKERS:
        assert marker not in html, f"raw {marker!r} in HTML:\n{html}"


@pytest.mark.parametrize(
    ("flavor", "expected"),
    [
        ("material", 'class="admonition warning"'),
        ("github", 'class="markdown-alert markdown-alert-warning"'),
        ("mdbook", 'class="markdown-alert markdown-alert-warning"'),
        ("myst", 'class="admonition warning"'),
    ],
)
def test_admonition_html_per_flavor(flavor: str, expected: str):
    node = mk.MkAdmonition("Careful **now**!", typ="warning")
    html = node.to_html_sync(flavor=flavor)
    assert expected in html
    assert "<strong>now</strong>" in html
    assert_rendered(html)


def test_active_flavor_is_used():
    node = mk.MkAdmonition("Careful!", typ="warning")
    with rendering.use(rendering.get_renderer("github")):
        html = node.to_html_sync()
    assert "markdown-alert-warning" in html


def test_myst_titled_admonition():
    node = mk.MkAdmonition("Body", typ="warning", title="Heads up")
    html = node.to_html_sync(flavor="myst")
    assert '<p class="admonition-title">Heads up</p>' in html
    assert_rendered(html)


def test_myst_dropdown_and_tabs():
    adm = mk.MkAdmonition("inner *text*", typ="note", title="More", collapsible=True)
    node = mk.MkTabbed({"First": "a text", "Second": adm})
    html = node.to_html_sync(flavor="myst")
    assert '<div class="sd-tab-set">' in html
    assert '<p class="sd-tab-label">Second</p>' in html
    assert "<details" in html
    assert "<summary>More</summary>" in html
    assert "<em>text</em>" in html
    assert_rendered(html)


def test_myst_code_block_with_caption():
    node = mk.MkCode("print(1)", language="py", title="t.py")
    html = node.to_html_sync(flavor="myst")
    assert '<div class="code-block-caption">t.py</div>' in html
    assert '<code class="language-py">print(1)' in html
    assert "{code-block}" not in html


def test_github_fallback_without_comrak(monkeypatch: pytest.MonkeyPatch):
    from mkconvert import ComrakParser

    monkeypatch.setattr(ComrakParser, "is_available", classmethod(lambda cls: False))
    html = html_render.comrak("Text", flavor="github")
    assert html.startswith("<!-- github flavour: comrak not installed")
    assert "<p>Text</p>" in html

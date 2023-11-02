from __future__ import annotations

import mknodes as mk


def test_empty():
    node = mk.MkText()
    assert not str(node)


def test_getitem_ending_with_eof():
    node = mk.MkText("## Test section\nTest")
    assert str(node["Test section"]) == "Test"


def test_getitem_ending_with_another_section():
    node = mk.MkText("## Test section\nTest\n## Another section")
    assert str(node["Test section"]) == "Test\n"


def test_fetch_from_url():
    url = "https://raw.githubusercontent.com/fire1ce/DDNS-Cloudflare-Bash/main/README.md"
    node = mk.MkText.from_url(url)
    assert str(node)


def test_rendered_children():
    node = mk.MkText("{{ 'Test' | MkAdmonition | MkAdmonition }}", render_jinja=True)
    num_desc = 3  # 2 * MkAdmonition, 1 * MkText
    assert len(node.children) == 1
    assert len(list(node.descendants)) == num_desc
    admon_inner = node.children[0]
    text_inner = admon_inner.children[0]
    assert admon_inner == text_inner.parent
    assert node == admon_inner.parent
    assert node.parent is None

    node = mk.MkText("{{ mk.MkAdmonition(mk.MkAdmonition('test')) }}", render_jinja=True)
    assert len(node.children) == 1
    assert len(list(node.descendants)) == num_desc
    admon_inner = node.children[0]
    text_inner = admon_inner.children[0]
    assert admon_inner == text_inner.parent
    assert node == admon_inner.parent
    assert node.parent is None

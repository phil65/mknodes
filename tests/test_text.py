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

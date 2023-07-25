from __future__ import annotations

from mknodes import __linkreplacer


class File:
    src_path = "test"


class Page:
    file = File()


def test_linkreplacer():
    replacer = __linkreplacer.LinkReplacerPlugin()
    replacer.on_page_markdown("test", page=Page(), config=dict(docs_dir=""), files=[])

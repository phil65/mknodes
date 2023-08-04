from __future__ import annotations

from mknodes import linkreplacerplugin


class File:
    src_uri = "test"


class Page:
    file = File()


def test_linkreplacer():
    replacer = linkreplacerplugin.LinkReplacerPlugin()
    replacer.on_page_markdown("test", page=Page(), config=dict(docs_dir=""), files=[])

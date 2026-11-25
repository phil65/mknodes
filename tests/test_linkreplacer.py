from __future__ import annotations

from mknodes.utils import linkreplacer


def test_bare_links_keep_anchors():
    replacer = linkreplacer.LinkReplacer()
    replacer.mapping["b.md"].append("sub/b.md")
    replacer.mapping["c.md"].append("sub/c.md")
    md = "[B](b.md#x), [C](c.md) and [D](missing.md)"
    result = replacer.replace(md, "a.md")
    assert result == "[B](sub/b.md#x), [C](sub/c.md) and `D`"

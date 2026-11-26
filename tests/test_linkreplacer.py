from mknodes.utils import linkreplacer


def test_bare_links_keep_anchors():
    replacer = linkreplacer.LinkReplacer()
    replacer.mapping["b.md"].append("sub/b.md")
    replacer.mapping["c.md"].append("sub/c.md")
    md = "[B](b.md#x), [C](c.md) and [D](missing.md)"
    result = replacer.replace(md, "a.md")
    assert result == "[B](sub/b.md#x), [C](sub/c.md) and `D`"


def test_ambiguous_filename_prefers_sibling():
    replacer = linkreplacer.LinkReplacer()
    replacer.mapping["mknode.md"] += ["nodes/mknode.md", "api/mknode.md"]
    assert replacer.replace("[x](mknode.md)", "api/index.md") == "[x](mknode.md)"
    assert replacer.replace("[x](mknode.md)", "other.md") == "[x](nodes/mknode.md)"

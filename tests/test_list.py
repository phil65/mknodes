from __future__ import annotations

import pytest

import mknodes as mk


EXPECTED = """## test

  * a
  * b
"""


def test_list():
    ls = mk.MkList()
    assert not str(ls)


def test_markdown():
    ls = mk.MkList(["a", "b"], header="test")
    assert str(ls) == EXPECTED


if __name__ == "__main__":
    pytest.main([__file__])


@pytest.mark.parametrize("flavor", ["material", "github"])
async def test_multi_line_items_are_indented(flavor: str):
    node = mk.MkList([mk.MkAdmonition("Nested!", typ="info"), "second"])
    md = await node.to_markdown(flavor=flavor)
    first, second = md.split("\n  * ")
    assert first.startswith("  * ")
    assert all(line.startswith("    ") for line in first.splitlines()[1:] if line)
    assert second.strip() == "second"

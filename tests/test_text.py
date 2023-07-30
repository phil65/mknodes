from __future__ import annotations

import mknodes


def test_empty():
    nav = mknodes.MkText()
    assert not str(nav)


def test_getitem_ending_with_eof():
    nav = mknodes.MkText("## Test section\nTest")
    assert str(nav["Test section"]) == "Test"


def test_getitem_ending_with_another_section():
    nav = mknodes.MkText("## Test section\nTest\n## Another section")
    assert str(nav["Test section"]) == "Test\n"

from __future__ import annotations

import mknodes as mk


EXPECTED = """!!! info
    This is a test
"""


def test_admonition():
    admonition = mk.MkAdmonition("")
    assert not str(admonition)


def test_markdown():
    admonition = mk.MkAdmonition("This is a test")
    assert str(admonition) == EXPECTED

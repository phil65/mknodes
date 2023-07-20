from __future__ import annotations

import mknodes


EXPECTED = """!!! info
    This is a test
"""


def test_admonition():
    admonition = mknodes.MkAdmonition("")
    assert not str(admonition)


def test_markdown():
    admonition = mknodes.MkAdmonition("This is a test")
    assert str(admonition) == EXPECTED

from __future__ import annotations

import mknodes


EXPECTED = """## Header

1.  abcde
    fghi
2.  abcde
    fghi
3.  abcde
    fghi
4.  abcde
    fghi
5.  abcde
    fghi
6.  abcde
    fghi
7.  abcde
    fghi
8.  abcde
    fghi
9.  abcde
    fghi
10. abcde
    fghi
"""


def test_empty():
    annotation = mknodes.MkAnnotations()
    assert not str(annotation)


def test_markdown():
    annotation = mknodes.MkAnnotations(["abcde\nfghi"] * 10, header="Header")
    assert str(annotation) == EXPECTED

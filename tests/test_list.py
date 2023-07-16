from __future__ import annotations

import markdownizer


def test_list():
    ls = markdownizer.List()
    assert not str(ls)

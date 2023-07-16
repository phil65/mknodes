from __future__ import annotations

import markdownizer


def test_text():
    nav = markdownizer.Text()
    assert not str(nav)

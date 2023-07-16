from __future__ import annotations

import markdownizer


def test_mkpage():
    page = markdownizer.MkPage()
    assert not str(page)

from __future__ import annotations

import mknodes


def test_page():
    page = mknodes.MkPage()
    assert not str(page)

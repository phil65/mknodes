from __future__ import annotations

import mknodes


def test_mkpage():
    page = mknodes.MkPage()
    assert not str(page)

from __future__ import annotations

import mknodes


def test_text():
    nav = mknodes.MkText()
    assert not str(nav)

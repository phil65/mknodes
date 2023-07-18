from __future__ import annotations

import mknodes


def test_text():
    nav = mknodes.Text()
    assert not str(nav)

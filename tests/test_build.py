from __future__ import annotations

import mknodes as mk


def test_build():
    from mknodes.manual import root

    nav = mk.MkNav()
    bld = root.Build()
    bld.on_root(nav)

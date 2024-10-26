from __future__ import annotations

import pytest

import mknodes as mk


def test_build():
    from mknodes.manual import root

    nav = mk.MkNav()
    bld = root.Build()
    bld.on_root(nav)


if __name__ == "__main__":
    pytest.main([__file__])

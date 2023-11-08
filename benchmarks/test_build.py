from __future__ import annotations

import pytest

import mknodes as mk


@pytest.mark.benchmark()
def test_build_duration():
    from mknodes.manual import root

    nav = mk.MkNav()
    bld = root.Build()
    bld.on_root(nav)
    # for node in proj.root.descendants:
    #     if not isinstance(node, mk.MkPage):
    #         continue
    #     node.to_markdown()

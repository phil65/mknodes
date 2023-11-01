from __future__ import annotations

import pytest

import mknodes as mk


@pytest.mark.benchmark()
def test_build_duration():
    theme = mk.MaterialTheme()
    from mknodes.manual import root

    proj = mk.Project(theme=theme)
    root.build(proj)
    # for node in proj.root.descendants:
    #     if not isinstance(node, mk.MkPage):
    #         continue
    #     node.to_markdown()

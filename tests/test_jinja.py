from __future__ import annotations

import mknodes as mk


def test_if_mknodes_parent_is_set(mknodes_project):
    page = mk.MkPage()
    mknodes_project._root += page
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert page.env.rendered_nodes[-1].parent == page

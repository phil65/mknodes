from __future__ import annotations

import mknodes


def test_if_mknodes_parent_is_set(project):
    page = mknodes.MkPage()
    project._root += page
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert page.env.rendered_nodes[-1].parent == page

from __future__ import annotations

import mknodes as mk


def test_if_mknodes_parent_is_set():
    page = mk.MkPage()
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert page.env.rendered_nodes[-1].parent == page


def test_correct_child_count_after_multiple_renders():
    page = mk.MkPage()
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert len(page.env.rendered_nodes) == 1
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert len(page.env.rendered_nodes) == 1
    env = page.env
    env.render_string(r"{{ 'test' | MkHeader }}")
    env.render_string(r"{{ 'test' | MkHeader }}")
    assert len(env.rendered_nodes) == 1

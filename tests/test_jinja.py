from __future__ import annotations

import pytest

import mknodes as mk


async def test_if_mknodes_parent_is_set():
    page = mk.MkPage()
    await page.env.render_string_async(r"{{ 'test' | MkHeader }}")
    assert page.env.rendered_nodes[-1].parent == page


async def test_correct_child_count_after_multiple_renders():
    page = mk.MkPage()
    await page.env.render_string_async(r"{{ 'test' | MkHeader }}")
    assert len(page.env.rendered_nodes) == 1
    await page.env.render_string_async(r"{{ 'test' | MkHeader }}")
    assert len(page.env.rendered_nodes) == 1
    env = page.env
    await env.render_string_async(r"{{ 'test' | MkHeader }}")
    await env.render_string_async(r"{{ 'test' | MkHeader }}")
    assert len(env.rendered_nodes) == 1


if __name__ == "__main__":
    pytest.main([__file__])

from __future__ import annotations

import asyncio
from concurrent.futures import ThreadPoolExecutor

import mknodes as mk


def test_sync_renders_in_threads_leave_asyncio_run_alone():
    original = asyncio.run

    def render(i: int) -> str:
        return mk.MkText(f"{{{{ 'text {i}' | MkAdmonition }}}}").env.render_string(
            f"{{{{ 'text {i}' | MkHeader }}}}"
        )

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(render, range(32)))
    assert asyncio.run is original
    assert all(f"text {i}" in r for i, r in enumerate(results))


def test_memoized_children_follow_text_changes():
    node = mk.MkText("{{ 'a' | MkHeader }}", render_jinja=True)
    first = node.get_children()
    assert [type(c).__name__ for c in first] == ["MkHeader"]
    assert node.get_children() is first  # memoized
    node.set_text("{{ 'b' | MkCode }} {{ 'c' | MkCode }}")
    assert [type(c).__name__ for c in node.get_children()] == ["MkCode", "MkCode"]

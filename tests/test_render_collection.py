"""Per-render node collection (`NodeEnvironment.render_nodes[_async]`) and render-once nodes."""

import asyncio
from concurrent.futures import ThreadPoolExecutor

import jinjarope
import pytest

import mknodes as mk
from mknodes import rendering
from mknodes.utils import coroutines


@pytest.fixture
def executions(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Record every Jinja execution (jinjarope level, below NodeEnvironment)."""
    calls: list[str] = []
    orig_t = jinjarope.Environment.render_template_async
    orig_s = jinjarope.Environment.render_string_async

    async def render_template_async(self, name, *args, **kwargs):
        calls.append(name)
        return await orig_t(self, name, *args, **kwargs)

    async def render_string_async(self, string, *args, **kwargs):
        calls.append(string)
        return await orig_s(self, string, *args, **kwargs)

    monkeypatch.setattr(jinjarope.Environment, "render_template_async", render_template_async)
    monkeypatch.setattr(jinjarope.Environment, "render_string_async", render_string_async)
    return calls


async def test_result_has_markdown_and_nodes():
    page = mk.MkPage()
    result = await page.env.render_nodes_async(string="{{ 'x' | MkText | MkAdmonition }}")
    assert result.markdown == "!!! info\n    x\n"
    text, admonition = result.nodes
    assert isinstance(text, mk.MkText)
    assert isinstance(admonition, mk.MkAdmonition)
    assert result.children == [admonition]  # the text got re-parented
    assert text.parent is admonition


async def test_set_attribute_macro_and_filter_block():
    template = """\
{% set n = "abc" | MkText %}{{ n._text | upper }}
{% macro box(t) %}{{ t | MkAdmonition }}{% endmacro %}{{ box("m") | indent(2, first=True) }}
{% filter upper %}{{ "f" | MkHeader }}{% endfilter %}"""
    result = await mk.MkPage().env.render_nodes_async(string=template)
    assert result.markdown == "ABC\n  !!! info\n      m\n\n## F"
    assert [type(n).__name__ for n in result.children] == ["MkText", "MkAdmonition", "MkHeader"]


async def test_nested_templates_keep_their_nodes():
    template = (
        """{{ mk.MkText("{{ 'inner' | MkHeader }}", render_jinja=True) }}{{ 'b' | MkCode }}"""
    )
    page = mk.MkPage()
    result = await page.env.render_nodes_async(string=template)
    text, code = result.children
    assert isinstance(text, mk.MkText)
    assert isinstance(code, mk.MkCode)
    assert [type(n).__name__ for n in text.get_children()] == ["MkHeader"]
    assert "## inner" in result.markdown


async def test_nested_render_of_same_env_counts_for_outer():
    """`render_string` filter used to reset the shared list of the outer render."""
    template = (
        """{{ 'a' | MkHeader }}{{ "{{ 'b' | MkCode }}" | render_string }}{{ 'c' | MkText }}"""
    )
    result = await mk.MkPage().env.render_nodes_async(string=template)
    # (Jinja calls `render_string` with a constant argument already at compile time.)
    assert sorted(type(n).__name__ for n in result.children) == ["MkCode", "MkHeader", "MkText"]


async def test_concurrent_renders_of_one_env_are_separate():
    page = mk.MkPage()
    results = await asyncio.gather(*[
        page.env.render_nodes_async(string=f"{{{{ 'n{i}' | MkText }}}}") for i in range(20)
    ])
    for i, result in enumerate(results):
        assert [n._text for n in result.nodes] == [f"n{i}"]

    def render(i: int):
        return page.env.render_nodes(string=f"{{{{ 't{i}' | MkHeader }}}}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        thread_results = list(pool.map(render, range(32)))
    for i, result in enumerate(thread_results):
        assert [n._text for n in result.nodes] == [f"t{i}"]


async def test_template_renders_once_for_children_and_content(executions: list[str]):
    node = mk.MkText("{{ 'x' | MkAdmonition }} {{ 'y' | MkCode }}", render_jinja=True)
    children = node.get_children()
    content = await node.get_content()
    assert len(executions) == 1
    assert node.get_children() is children
    assert content.markdown.startswith("!!! info\n    x")


async def test_template_rerenders_after_attribute_change(executions: list[str]):
    node = mk.MkText("{{ 'x' | MkHeader }}", render_jinja=True)
    assert len(node.get_children()) == 1
    node.set_text("{{ 'a' | MkCode }}{{ 'b' | MkCode }}")
    assert len(node.get_children()) == 2  # noqa: PLR2004
    assert len(executions) == 2  # noqa: PLR2004


async def test_render_is_cached_per_flavor(executions: list[str]):
    node = mk.MkText("{{ 'hi' | MkAdmonition(typ='bug') }}", render_jinja=True)
    children = node.get_children()
    assert (await node.to_markdown()).startswith("!!! bug")
    assert (await node.to_markdown(flavor="github")).strip() == "> [!CAUTION]\n> hi"
    assert len(executions) == 2  # material (tree + content), github (content)  # noqa: PLR2004
    assert node.get_children() is children


async def test_node_output_renders_in_running_loop(monkeypatch: pytest.MonkeyPatch):
    """`{{ node }}` is awaited by the template code: no run_sync thread per node."""
    calls = []
    orig = coroutines.run_sync

    def run_sync(coro):
        calls.append(coro)
        return orig(coro)

    monkeypatch.setattr(coroutines, "run_sync", run_sync)
    with rendering.use(rendering.get_renderer("github")):
        text = await mk.MkContainer().env.render_string_async(
            "{{ 'hi' | MkAdmonition(typ='bug') }}{{ mk.MkHeader('x', level=3) }}"
        )
    assert text == "> [!CAUTION]\n> hi\n### x"
    assert calls == []

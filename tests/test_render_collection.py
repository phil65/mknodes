"""Per-render node collection (`NodeEnvironment.render_nodes`) and render-once nodes."""

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
    orig_t = jinjarope.Environment.render_template
    orig_s = jinjarope.Environment.render_string

    def render_template(self, name, *args, **kwargs):
        calls.append(name)
        return orig_t(self, name, *args, **kwargs)

    def render_string(self, string, *args, **kwargs):
        calls.append(string)
        return orig_s(self, string, *args, **kwargs)

    monkeypatch.setattr(jinjarope.Environment, "render_template", render_template)
    monkeypatch.setattr(jinjarope.Environment, "render_string", render_string)
    return calls


def test_result_has_markdown_and_nodes():
    page = mk.MkPage()
    result = page.env.render_nodes(string="{{ 'x' | MkText | MkAdmonition }}")
    assert result.markdown == "!!! info\n    x\n"
    text, admonition = result.nodes
    assert isinstance(text, mk.MkText)
    assert isinstance(admonition, mk.MkAdmonition)
    assert result.children == [admonition]  # the text got re-parented
    assert text.parent is admonition


def test_set_attribute_macro_and_filter_block():
    template = """\
{% set n = "abc" | MkText %}{{ n._text | upper }}
{% macro box(t) %}{{ t | MkAdmonition }}{% endmacro %}{{ box("m") | indent(2, first=True) }}
{% filter upper %}{{ "f" | MkHeader }}{% endfilter %}"""
    result = mk.MkPage().env.render_nodes(string=template)
    assert result.markdown == "ABC\n  !!! info\n      m\n\n## F"
    assert [type(n).__name__ for n in result.children] == ["MkText", "MkAdmonition", "MkHeader"]


def test_nested_templates_keep_their_nodes():
    template = (
        """{{ mk.MkText("{{ 'inner' | MkHeader }}", render_jinja=True) }}{{ 'b' | MkCode }}"""
    )
    page = mk.MkPage()
    result = page.env.render_nodes(string=template)
    text, code = result.children
    assert isinstance(text, mk.MkText)
    assert isinstance(code, mk.MkCode)
    assert [type(n).__name__ for n in text.get_children()] == ["MkHeader"]
    assert "## inner" in result.markdown


def test_nested_render_of_same_env_counts_for_outer():
    """`render_string` filter used to reset the shared list of the outer render."""
    template = (
        """{{ 'a' | MkHeader }}{{ "{{ 'b' | MkCode }}" | render_string }}{{ 'c' | MkText }}"""
    )
    result = mk.MkPage().env.render_nodes(string=template)
    # (Jinja calls `render_string` with a constant argument already at compile time.)
    assert sorted(type(n).__name__ for n in result.children) == ["MkCode", "MkHeader", "MkText"]


def test_concurrent_renders_of_one_env_are_separate():
    page = mk.MkPage()
    results = [page.env.render_nodes(string=f"{{{{ 'n{i}' | MkText }}}}") for i in range(20)]
    for i, result in enumerate(results):
        assert [n._text for n in result.nodes] == [f"n{i}"]

    def render(i: int):
        return page.env.render_nodes(string=f"{{{{ 't{i}' | MkHeader }}}}")

    with ThreadPoolExecutor(max_workers=8) as pool:
        thread_results = list(pool.map(render, range(32)))
    for i, result in enumerate(thread_results):
        assert [n._text for n in result.nodes] == [f"t{i}"]


def test_template_renders_once_for_children_and_content(executions: list[str]):
    node = mk.MkText("{{ 'x' | MkAdmonition }} {{ 'y' | MkCode }}", render_jinja=True)
    children = node.get_children()
    content = node.get_content()
    assert len(executions) == 1
    assert node.get_children() is children
    assert content.markdown.startswith("!!! info\n    x")


def test_template_rerenders_after_attribute_change(executions: list[str]):
    node = mk.MkText("{{ 'x' | MkHeader }}", render_jinja=True)
    assert len(node.get_children()) == 1
    node.set_text("{{ 'a' | MkCode }}{{ 'b' | MkCode }}")
    assert len(node.get_children()) == 2  # noqa: PLR2004
    assert len(executions) == 2  # noqa: PLR2004


def test_render_is_cached_per_flavor(executions: list[str]):
    node = mk.MkText("{{ 'hi' | MkAdmonition(typ='bug') }}", render_jinja=True)
    children = node.get_children()
    assert (node.to_markdown()).startswith("!!! bug")
    assert (node.to_markdown(flavor="github")).strip() == "> [!CAUTION]\n> hi"
    assert len(executions) == 2  # material (tree + content), github (content)  # noqa: PLR2004
    assert node.get_children() is children


def test_node_output_renders_without_event_loops(monkeypatch: pytest.MonkeyPatch):
    """`{{ node }}` renders synchronously: no run_sync thread / event loop per node."""
    calls = []
    orig = coroutines.run_sync

    def run_sync(coro):
        calls.append(coro)
        return orig(coro)

    monkeypatch.setattr(coroutines, "run_sync", run_sync)
    with rendering.use(rendering.get_renderer("github")):
        text = mk.MkContainer().env.render_string(
            "{{ 'hi' | MkAdmonition(typ='bug') }}{{ mk.MkHeader('x', level=3) }}"
        )
    assert text == "> [!CAUTION]\n> hi\n### x"
    assert calls == []

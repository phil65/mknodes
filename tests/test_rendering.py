import pytest

import mknodes as mk
from mknodes import rendering


def test_default_flavor_is_material():
    node = mk.MkAdmonition("text", typ="warning")
    assert isinstance(rendering.current(), rendering.MaterialRenderer)
    assert (node.to_markdown()).startswith("!!! warning")
    assert node.to_markdown(flavor="material") == node.to_markdown()


def test_unknown_flavor():
    with pytest.raises(ValueError, match="Unknown flavor"):
        mk.MkText("x").to_markdown(flavor="nope")


def test_github_admonition():
    node = mk.MkAdmonition("Be careful.", typ="danger", title="Careful")
    md = node.to_markdown(flavor="github")
    assert md == "> [!CAUTION]\n> **Careful**\n>\n> Be careful.\n"


def test_github_collapsible_admonition():
    node = mk.MkAdmonition("folded", collapsible=True, title="More", expanded=True)
    md = node.to_markdown(flavor="github")
    assert md.startswith("<details open>\n<summary>More</summary>\n\nfolded")


def test_github_nested_nodes_use_parent_flavor():
    tabs = mk.MkTabbed({"A": mk.MkKeys("ctrl+a"), "B": "text"})
    node = mk.MkAdmonition(["intro", tabs], typ="tip")
    md = node.to_markdown(flavor="github")
    assert md.startswith("> [!TIP]\n> intro")
    assert "> <details open>\n> <summary>A</summary>" in md
    assert "<kbd>Ctrl</kbd>+<kbd>A</kbd>" in md
    assert "===" not in md
    assert "++" not in md


def test_github_container_page():
    page = mk.MkPage("p", content=[mk.MkCode("x = 1", language="py", title="a.py")])
    md = page.to_markdown(flavor="github")
    assert "**a.py**\n\n```py\nx = 1\n```" in md


def test_flavor_reaches_jinja_rendered_nodes():
    """Nodes rendered via str() in Jinja (run_sync in a thread) keep the flavour."""
    parent = mk.MkContainer()
    with rendering.use(rendering.get_renderer("github")):
        text = parent.env.render_string("{{ 'hi' | MkAdmonition(typ='bug') }}")
    assert text.strip() == "> [!CAUTION]\n> hi"


def test_flavor_is_reset_after_render():
    node = mk.MkAdmonition("x")
    node.to_markdown(flavor="github")
    assert (node.to_markdown()).startswith("!!! info")


def test_nodefile_template_serves_as_rule():
    """MkImage has an [output.github] template in its node file and no Python rule."""
    github = rendering.get_renderer_class("github")
    assert mk.MkImage not in github._rules
    assert github.supports(mk.MkImage)
    md = mk.MkImage("img.png", caption="cap").to_markdown(flavor="github")
    assert '<img alt="cap" src="img.png">' in md


def test_css_classes_are_dropped_for_github():
    node = mk.MkText("text")
    node.add_css_class("fancy")
    assert "{: .fancy}" in node.to_markdown()
    assert node.to_markdown(flavor="github") == "text"


def test_rule_lookup_walks_node_hierarchy():
    class Base(mk.MkText):
        pass

    class Child(Base):
        pass

    class SelfRendering(Child):
        def to_md_unprocessed(self) -> str:
            return "self"

    class Flavor(rendering.Renderer):
        name = "test-flavor"

    @Flavor.rule(Base)
    def render_base(node, r):
        return "rule"

    assert Child("x").to_markdown(flavor=Flavor()) == "rule"
    # A subclass rendering itself is not covered by the rule of its base class.
    assert SelfRendering("x").to_markdown(flavor=Flavor()) == "self"


def test_doc_builder_flavor():
    from mknodes.build.builder import DocBuilder

    nav = mk.MkNav()
    nav += mk.MkPage("index", content=mk.MkAdmonition("hi", typ="warning"))
    output = DocBuilder(render_jinja=False, flavor="github").build(nav)
    assert "> [!WARNING]\n> hi" in output.files["index.md"]


def test_github_page_title_instead_of_front_matter():
    page = mk.MkPage("Intro", content="text")
    page.metadata.hide = ["toc"]
    assert (page.to_markdown()).startswith("---")
    assert page.to_markdown(flavor="github") == "# Intro\n\ntext"
    page = mk.MkPage("Intro", content="# Own title\n\ntext")
    assert (page.to_markdown(flavor="github")).startswith("# Own title")


def test_github_api_docs_from_griffe():
    md = mk.MkDocStrings("mknodes.rendering.base.Renderer").to_markdown(flavor="github")
    assert ":::" not in md
    path = "mknodes.rendering.base.Renderer"
    assert md.startswith(f'<a id="{path}"></a>\n\n```python\nclass Renderer\n```')
    heading = f'## <a id="{path}.find_rule"></a>`find_rule`'
    assert f"{heading}\n\n```python\ndef find_rule(node_type: type) -> Rule | None\n```" in md
    assert "def rule(*node_types: type) -> Callable[[R], R]" in md
    assert "_lookup_cache" not in md  # private


def test_api_docs_sections_and_options():
    from mknodes.info import grifferegistry
    from mknodes.rendering import apidocs

    fn = grifferegistry.registry.get_module("mknodes.rendering.apidocs")["render"]
    md = apidocs.render(fn, {"show_root_heading": True, "heading_level": 3})
    path = "mknodes.rendering.apidocs.render"
    assert md.startswith(f'### <a id="{path}"></a>`{path}`')
    mod = grifferegistry.registry.get_module("mknodes.rendering")
    md = apidocs.render(mod, {"members": ["use"]})
    assert '## <a id="mknodes.rendering.use"></a>`use`' in md
    assert "`current`" not in md
    func = grifferegistry.registry.get_module("mknodes.rendering")["get_renderer_class"]
    md = apidocs.render(func, {})
    assert "**Parameters:**" not in md  # no Args section in that docstring
    md = apidocs.render(grifferegistry.registry.get_module("mknodes.rendering.base")["use"], {})
    assert "def use(renderer: Renderer) -> Generator[Renderer]" in md


def test_github_icons_become_iconify_images():
    link = mk.MkLink("https://x.org", "Source", icon="fa-brands:github")
    md = link.to_markdown(flavor="github")
    assert md == (
        '[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github">'
        " Source](https://x.org)"
    )
    icon = mk.MkIcon("mdi:wrench", color="#ff0000")
    md = icon.to_markdown(flavor="github")
    assert md.startswith(
        '<img src="https://api.iconify.design/mdi/wrench.svg?height=24&color=%23ff0000"'
    )


MATERIAL_TEXT = """\
Intro

!!! info "Heads up"
    Line one.

    !!! warning
        nested

=== "One"
    first

=== "Two"
    second

```md
!!! note
    stays
```"""


def test_github_converts_handwritten_material_blocks():
    from mknodes.rendering import github, materialtext

    page = mk.MkPage("P", content=MATERIAL_TEXT)
    md = page.to_markdown(flavor="github")
    assert "> [!NOTE]\n> **Heads up**\n>\n> Line one.\n>\n> > [!WARNING]\n> > nested" in md
    assert "<details open>\n<summary>One</summary>\n\nfirst" in md
    assert "<details>\n<summary>Two</summary>" in md
    assert "```md\n!!! note\n    stays\n```" in md  # fences untouched
    assert materialtext.convert(md, github.MATERIAL_CONVERTERS) == md  # idempotent
    assert "!!! info" in page.to_markdown()  # material: unchanged


def test_github_material_badge():
    badge = mk.MkMaterialBadge("mdi:flag", text="Flag", target="https://x.org")
    md = badge.to_markdown(flavor="github")
    assert md == (
        '[<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag">'
        " <code>Flag</code>](https://x.org)"
    )


def test_api_docs_skip_cyclic_aliases(tmp_path, monkeypatch):
    """An import shadowing a class (here: in an `if __name__` block) must not break the docs."""
    import griffe

    from mknodes.rendering import apidocs

    pkg = tmp_path / "cyclicpkg"
    pkg.mkdir()
    (pkg / "__init__.py").write_text('from cyclicpkg.mod import Thing\n\n__all__ = ["Thing"]\n')
    (pkg / "mod.py").write_text(
        '__all__ = ["Thing"]\n\n\nclass Thing:\n    """A thing."""\n\n\n'
        'if __name__ == "__main__":\n    from cyclicpkg import Thing\n'
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    module = griffe.load("cyclicpkg", search_paths=[str(tmp_path)])
    for target in (module, module["mod"]):  # raised CyclicAliasError before
        assert isinstance(apidocs.render(target, {"show_submodules": True}), str)


def test_mkllm_without_agentpool(monkeypatch):
    """A missing / broken optional LLM dependency must not break the build."""
    import sys

    from mknodes.templatenodes import mkllm

    monkeypatch.setitem(sys.modules, "agentpool", None)  # makes `import agentpool` fail
    monkeypatch.setitem(sys.modules, "agentpool.functional", None)
    assert mk.MkLlm("Say hi").to_markdown() == mkllm.UNAVAILABLE_TEXT

from __future__ import annotations

import logging

import pytest

import mknodes as mk
from mknodes.build import BuildOutput, refcheck


def check(pages: dict[str, str], **kwargs) -> list[refcheck.RefIssue]:
    return refcheck.check_output(BuildOutput(pages=pages), **kwargs)


def test_find_references_skips_code_and_link_definitions():
    md = """\
[A][mknodes.MkText] and `[B][mknodes.Nope]`
[C][label]

```py
[D][mknodes.Nope]
```

[label]: https://example.com
[E][]
"""
    refs = list(refcheck.find_references(md))
    assert refs == [(1, "A", "mknodes.MkText"), (9, "E", "E")]


def test_fences_close_only_with_the_same_fence():
    # superfences: a longer fence inside a fence does not close it
    md = "```md\n```` mermaid\n````\n```\n::: mknodes.MkText\n"
    directives = refcheck.find_directives(md)
    assert [d.identifier for d in directives] == ["mknodes.MkText"]


def test_find_directives_anchor_options():
    md = """\
::: mknodes.MkText

    ::: mknodes.MkHeader
        options:
          show_root_toc_entry: False

::: mknodes.MkCode
    options:
      show_root_toc_entry: False
      show_root_heading: True
"""
    directives = refcheck.find_directives(md)
    anchored = {d.identifier: d.anchored for d in directives}
    assert anchored == {"mknodes.MkText": True, "mknodes.MkHeader": False, "mknodes.MkCode": True}


def test_resolvable_references():
    pages = {
        "api.md": "::: mknodes.basenodes.mkcontainer.MkContainer\n",
        "page.md": (
            "[a][mknodes.basenodes.mkcontainer.MkContainer]\n"  # rendered path
            "[b][mknodes.MkContainer]\n"  # public alias of the rendered object
            "[c][mknodes.basenodes.mkcontainer.MkContainer.get_items]\n"  # member
            "[d][heading-slug]\n"  # not a dotted path
            "[e][otherpackage.Klass]\n"  # package not documented on this site
        ),
    }
    assert check(pages) == []


def test_member_of_import_alias_gets_fixed():
    # mkdocstrings registers `mknodes.MkContainer` (alias of the rendered class), but not
    # `mknodes.MkContainer.get_items` (verified with zensical 0.1.3)
    pages = {
        "api.md": "::: mknodes.basenodes.mkcontainer.MkContainer\n",
        "page.md": "text\n[c][mknodes.MkContainer.get_items] and [c][mknodes.MkContainer.get_items]",
    }
    output = BuildOutput(pages=dict(pages))
    issues = refcheck.check_output(output)
    assert len(issues) == 2  # noqa: PLR2004
    assert all(i.fixable for i in issues)
    assert issues[0].suggestion == "mknodes.basenodes.mkcontainer.MkContainer.get_items"
    fixed = refcheck.fix_references(output, issues)
    assert fixed == issues
    expected = "[c][mknodes.basenodes.mkcontainer.MkContainer.get_items]"
    assert output.pages["page.md"] == f"text\n{expected} and {expected}"
    assert refcheck.check_output(output) == []


def test_blocks_in_raw_html_are_not_rendered():
    md = "<div markdown='1'>\n\n::: mknodes.MkNav\n\n</div>\n\n::: mknodes.MkText\n"
    assert [d.identifier for d in refcheck.find_directives(md)] == ["mknodes.MkText"]


def test_unrendered_object_is_reported():
    pages = {"api.md": "::: mknodes.MkText\n", "page.md": "x\n[Nav][mknodes.MkNav]\n"}
    (issue,) = check(pages)
    assert issue.page == "page.md"
    assert issue.line == 2  # noqa: PLR2004
    assert issue.identifier == "mknodes.MkNav"
    assert "mknodes.navs.mknav.MkNav" in issue.reason
    assert str(issue).startswith("page.md:2: unresolved reference [Nav][mknodes.MkNav]")


def test_hidden_root_has_no_anchor():
    md = "::: mknodes.Metadata\n    options:\n      show_root_toc_entry: False\n"
    pages = {"meta.md": md, "page.md": "[a][mknodes.Metadata] [b][mknodes.Metadata.status]"}
    issues = [i for i in check(pages) if i.page == "page.md"]
    assert [i.identifier for i in issues] == ["mknodes.Metadata"]


def test_inherited_member_suggests_defining_class():
    pages = {
        "a.md": "::: mknodes.MkPage\n",
        "b.md": "::: mknodes.basenodes.mkcontainer.MkContainerBase\n",
        "page.md": "[append][mknodes.MkPage.append]",
    }
    (issue,) = check(pages)
    assert "inherited" in issue.reason
    assert issue.suggestion == "mknodes.basenodes.mkcontainer.MkContainerBase.append"
    assert issue.fixable


def test_typo_gets_suggestion():
    pages = {"api.md": "::: mknodes.MkText\n", "page.md": "[t][mknodes.MkTxt]"}
    (issue,) = check(pages)
    assert "does not exist" in issue.reason
    assert issue.suggestion == "mknodes.MkText"


def test_inventory_and_packages():
    pages = {"page.md": "[a][mknodes.MkNav] [b][mknodes.MkText]"}
    assert check(pages) == []  # no `:::` block of mknodes: not validated
    issues = check(pages, packages=["mknodes"], inventory={"mknodes.MkText"})
    assert [i.identifier for i in issues] == ["mknodes.MkNav"]


def test_docstring_references_are_checked(monkeypatch: pytest.MonkeyPatch):
    checker = refcheck.RefChecker()
    checker.add_page("api.md", "::: mknodes.MkText\n")
    checker._collect()
    obj, page = checker.rendered["mknodes.basenodes.mktext.MkText"]
    monkeypatch.setattr(
        refcheck,
        "_docstring",
        lambda o: ("See [MkNav][mknodes.MkNav].", "mktext.py:3") if o is obj else ("", None),
    )
    (issue,) = checker.check_docstrings()
    assert issue.page == page == "api.md"
    assert issue.identifier == "mknodes.MkNav"
    assert issue.origin == "mktext.py:3"
    assert issue.node == "docstring of mknodes.basenodes.mktext.MkText"


def test_origin_is_reported(tmp_path):
    import jinja2

    (tmp_path / "tpl.jinja").write_text("intro\n\n[Nav][mknodes.MkNav] and [Nav][mknodes.MkNav]\n")
    page = mk.MkPage("page")
    node = mk.MkTemplate("tpl.jinja")
    page += node
    node.env.loader = jinja2.FileSystemLoader(str(tmp_path))
    origin, desc = refcheck.find_origin(page, "Nav", "mknodes.MkNav", occurrence=1)
    assert origin is not None
    assert origin.endswith("tpl.jinja:3")
    assert desc == "MkTemplate('tpl.jinja')"


def test_commented_code_origin():
    def build(page: mk.MkPage) -> None:
        # See [MkNav][mknodes.MkNav].
        page += "x"

    page = mk.MkPage("page")
    page += mk.MkCommentedCode(build, style="text")
    origin, desc = refcheck.find_origin(page, "MkNav", "mknodes.MkNav")
    assert origin is not None
    assert origin.split(":")[0].endswith("test_refcheck.py")
    assert desc == "MkCommentedCode(test_commented_code_origin.<locals>.build)"


def test_generator_logs_issues(caplog: pytest.LogCaptureFixture):
    from mknodes.site import GeneratorSettings, generator

    gen = generator.SiteGenerator(GeneratorSettings())
    root = mk.MkNav()
    output = BuildOutput(pages={"api.md": "::: mknodes.MkText\n", "p.md": "[N][mknodes.MkNav]"})
    with caplog.at_level(logging.WARNING, logger="mknodes"):
        issues = gen.check_references(output, root)
    assert len(issues) == 1
    assert "p.md:1: unresolved reference [N][mknodes.MkNav]" in caplog.text


if __name__ == "__main__":
    pytest.main([__file__])


def test_link_references():
    api = '## <a id="mknodes.MkNav"></a>`mknodes.MkNav`\n\n### <a id="mknodes.MkNav.add_page"></a>'
    pages = {
        "api/navs.md": api,
        "tour.md": '<a id="mknodes.MkNav"></a>\n\n[nav][mknodes.MkNav]',
        "guide/usage.md": """\
[MkNav][mknodes.MkNav], [add_page][mknodes.MkNav.add_page], [`MkNav`][mknodes.navs.mknav.MkNav]
[parse][mknodes.MkNav.parse] (member without anchor: its class)
[MkText][mknodes.MkText], [some text][mknodes.Nope], [heading][some-heading]
`[a][mknodes.MkNav]` and [label][mknodes.Label]

[mknodes.label]: https://example.com
""",
    }
    output = BuildOutput(pages=pages)
    refcheck.link_references(output, inventory={"mknodes.MkText": "https://x.org/#MkText"})
    lines = output.pages["guide/usage.md"].splitlines()
    url = "../api/navs.md#mknodes.MkNav"
    member_url = "../api/navs.md#mknodes.MkNav.add_page"
    assert lines[0] == f"[MkNav]({url}), [add_page]({member_url}), [`MkNav`]({url})"
    assert lines[1] == f"[parse]({url}) (member without anchor: its class)"
    assert lines[2] == "[MkText](https://x.org/#MkText), some text, [heading][some-heading]"
    assert lines[3] == "`[a][mknodes.MkNav]` and [label][mknodes.Label]"
    # A heading wins over an object rendered without one.
    assert output.pages["tour.md"].endswith(f"[nav]({url.removeprefix('../')})")
    assert "[" not in refcheck.ReferenceLinker({}).link("[MkFoo][mknodes.MkFoo]", "a.md")


async def test_github_build_links_references():
    from mknodes.build.builder import DocBuilder

    nav = mk.MkNav()
    nav += mk.MkPage("api", content=mk.MkDocStrings("mknodes.rendering.use"))
    nav += mk.MkPage("guide", content="See [use][mknodes.rendering.use].")
    output = await DocBuilder(render_jinja=False, flavor="github").build(nav)
    assert "See [use](api.md#mknodes.rendering.use)." in output.pages["guide.md"]
    output = await DocBuilder(render_jinja=False).build(nav)
    assert "See [use][mknodes.rendering.use]." in output.pages["guide.md"]

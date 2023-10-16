from __future__ import annotations

import mknodes as mk


def build(project):
    root = project.get_root()
    sub_nav = mk.MkNav("Sub nav")
    sub_nav.page_template.announcement_bar = "Hello"
    sub_nav += mk.MkPage("Test page")
    root += sub_nav


def test_templates():
    theme = mk.MaterialTheme()
    project = mk.Project(theme=theme, repo=".", build_fn=build)
    project.build()
    assert project._root
    resources = project._root.get_resources()
    assert len(resources.templates) == 1
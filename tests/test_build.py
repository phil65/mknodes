from __future__ import annotations

import mknodes as mk


def build(project):
    sub_nav = mk.MkNav("Sub nav")
    sub_nav.page_template.announcement_bar = "Hello"
    sub_nav += mk.MkPage("Test page")
    project.root += sub_nav


# def test_templates():
#     theme = mk.MaterialTheme()
#     project = mk.Project(theme=theme, repo=".", build_fn=build)
#     assert project._root
#     project._root.get_resources()
#     assert len([i for i in resources.templates if i]) == 1

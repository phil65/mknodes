from __future__ import annotations

import mknodes as mk


def build(project):
    sub_nav = mk.MkNav("Sub nav")
    sub_nav.page_template.announcement_bar = "Hello"
    sub_nav += mk.MkPage("Test page")
    project.root += sub_nav


def test_build():
    from mknodes.manual import root

    nav = mk.MkNav()
    bld = root.Build()
    bld.on_root(nav)

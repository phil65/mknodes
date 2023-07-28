from __future__ import annotations

import mknodes

from mknodes import manual


def test_example_page_1():
    root_nav = mknodes.MkNav()
    manual.create_nodes_section(root_nav)


def test_example_page_2():
    root_nav = mknodes.MkNav()
    manual.create_documentation_section(root_nav)


def test_example_page_3():
    root_nav = mknodes.MkNav()
    manual.create_internals_section(root_nav)

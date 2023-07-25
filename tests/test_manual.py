from __future__ import annotations

import mknodes

from mknodes import manual


def test_example_page_1():
    root_nav = mknodes.MkNav()
    manual.create_page_1(root_nav)


def test_example_page_2():
    root_nav = mknodes.MkNav()
    manual.create_page_2(root_nav)


def test_example_page_3():
    root_nav = mknodes.MkNav()
    manual.create_page_3(root_nav)

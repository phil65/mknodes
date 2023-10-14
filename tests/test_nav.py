from __future__ import annotations

import pytest

import mknodes as mk


TREE_NUM_PAGES = 5
TREE_NUM_NAVS = 3
TREE_NUM_TEXT = 5
TREE_TOTAL = TREE_NUM_PAGES + TREE_NUM_NAVS + TREE_NUM_TEXT


def test_nav():
    nav = mk.MkNav()
    nav.add_doc(mk)
    nav.add_page("Test")
    nav.add_page("Test Index page", is_index=True)
    nav.add_nav("sub")


def test_from_folder(test_data_dir):
    nav = mk.MkNav()
    nav.parse.folder(test_data_dir / "nav_tree")
    assert len(list(nav.descendants)) == TREE_TOTAL - 1


def test_from_file(test_data_dir):
    nav_file = test_data_dir / "nav_tree/SUMMARY.md"
    nav = mk.MkNav()
    nav.parse.file(nav_file)
    assert len(list(nav.descendants)) == TREE_TOTAL - 1


def test_resolved_path():
    nav = mk.MkNav()
    subnav = nav.add_nav("subsection")
    subsubnav = subnav.add_nav("subsubsection")
    assert subsubnav.resolved_parts == ("subsection", "subsubsection")


def test_creating_module_document():
    nav = mk.MkNav()
    subnav = nav.add_nav("subsection")
    module_docs = subnav.add_doc(pytest)
    klasses = list(module_docs.iter_classes())
    assert klasses

from __future__ import annotations

import pytest

import mknodes


TREE_NUM_PAGES = 5
TREE_NUM_NAVS = 3
TREE_NUM_TEXT = 5
TREE_TOTAL = TREE_NUM_PAGES + TREE_NUM_NAVS + TREE_NUM_TEXT


def test_nav():
    nav = mknodes.MkNav()
    nav.add_doc(mknodes)
    nav.add_page("Test")
    nav.add_index_page("Test Index page")
    nav.add_nav("sub")


def test_from_folder(test_data_dir):
    nav = mknodes.MkNav()
    nav.parse.folder(test_data_dir / "nav_tree")
    assert len(list(nav.descendants)) == TREE_TOTAL - 1


def test_from_file(test_data_dir):
    nav_file = test_data_dir / "nav_tree/SUMMARY.md"
    nav = mknodes.MkNav()
    nav.parse.file(nav_file)
    assert len(list(nav.descendants)) == TREE_TOTAL - 1


def test_resolved_path():
    nav = mknodes.MkNav()
    subnav = nav.add_nav("subsection")
    subsubnav = subnav.add_nav("subsubsection")
    assert subsubnav.resolved_parts == ("subsection", "subsubsection")


def test_creating_module_document():
    nav = mknodes.MkNav()
    subnav = nav.add_nav("subsection")
    module_docs = subnav.add_doc(pytest)
    klasses = list(module_docs.iter_classes())
    assert klasses

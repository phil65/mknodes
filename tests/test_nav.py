from __future__ import annotations

import pytest

import mknodes


def test_nav():
    nav = mknodes.MkNav()
    nav.add_doc(mknodes)
    nav.add_page("Test")
    nav.add_index_page()
    nav.add_nav("sub")


def test_from_file(test_data_dir):
    nav = mknodes.MkNav.from_folder(test_data_dir / "nav_tree")
    assert len(list(nav.descendants)) == 9  # noqa: PLR2004


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

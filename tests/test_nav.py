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
    assert module_docs.get_children()


def test_cli_nav():
    nav = mk.MkCliNav("mknodes.cli:cli", section_name="CLI")
    assert nav.cli_info is not None
    assert nav.cli_info.subcommands
    children = nav.get_children()
    assert children


@pytest.fixture
def doc_package(tmp_path, monkeypatch):
    pkg = tmp_path / "docpkg"
    (pkg / "sub").mkdir(parents=True)
    (pkg / "__init__.py").write_text("")
    (pkg / "broken.py").write_text("raise ImportError('optional dependency missing')\n")
    (pkg / "sub" / "impl.py").write_text("class Foo:\n    pass\n")
    (pkg / "sub" / "__init__.py").write_text(
        "from docpkg.sub.impl import Foo\n\n__all__ = ['Foo']\n"
    )
    monkeypatch.syspath_prepend(str(tmp_path))
    return "docpkg"


def test_doc_not_recursive_skips_submodules(doc_package):
    nav = mk.MkNav()
    docs = nav.add_doc(doc_package)
    children = docs.get_children()  # must not import docpkg.broken
    assert not [c for c in children if isinstance(c, mk.MkDoc)]


if __name__ == "__main__":
    pytest.main([__file__])

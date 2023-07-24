from __future__ import annotations

import mknodes


def test_nav():
    nav = mknodes.MkNav()
    nav.add_doc(mknodes)
    nav.add_page("Test")
    nav.add_index_page()
    nav.add_nav("sub")


def test_from_file(test_data_dir):
    nav = mknodes.MkNav.from_folder(test_data_dir / "nav_tree")
    assert len(list(nav.descendants)) == 9

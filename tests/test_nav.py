from __future__ import annotations

import mknodes


def test_nav():
    nav = mknodes.MkNav()
    # nav_file = pathlib.Path(__file__).parent / "SUMMARY.md"
    # # print(pathlib.Path(nav_file).read_text())
    # nav = MkNav.from_file(pathlib.Path(__file__).parent / "SUMMARY.md", None)
    # lines = [f"{level * '    '} {node!r}" for level, node in nav.iter_nodes()]
    # print("\n".join(lines))

def test_from_file(test_data_dir):
    nav = mknodes.MkNav.from_folder(test_data_dir / "nav_tree")
    assert len(list(nav.descendants)) == 9

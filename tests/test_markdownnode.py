from __future__ import annotations

import mknodes


def test_virtual_files():
    nav = mknodes.MkNav()
    subnav = nav.add_nav("subsection")
    page = subnav.add_page("page")
    img = mknodes.MkBinaryImage(data=b"", path="Test.jpg")
    page.append(img)

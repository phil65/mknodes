from __future__ import annotations

import markdownizer


def test_virtual_files():
    nav = markdownizer.Nav()
    subnav = nav.add_nav("subsection")
    page = subnav.add_page("page")
    img = markdownizer.BinaryImage(data=b"", path="Test.jpg")
    page.append(img)

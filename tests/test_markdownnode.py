from __future__ import annotations

import markdownizer


def test_virtual_files():
    nav = markdownizer.Nav()
    subnav = nav.create_nav("subsection")
    page = subnav.create_page("page")
    img = markdownizer.BinaryImage(data=bytes(), path="Test.jpg")
    page.append(img)

from __future__ import annotations

import mknodes as mk


def test_page():
    page = mk.MkPage()
    page.metadata.pop("created")
    assert not str(page)


def test_next_and_previous_page():
    nav = mk.MkNav()
    page_1 = nav.add_page("Page 1")
    page_2 = nav.add_page("Page 2")
    assert page_1.previous_page is None
    assert page_1.next_page is page_2
    assert page_2.previous_page is page_1
    assert page_2.next_page is None


def test_next_and_previous_page_across_navs():
    nav = mk.MkNav()
    sub_1 = nav.add_nav("Sub 1")
    sub_2 = nav.add_nav("Sub 2")
    page_1 = sub_1.add_page("Page 1")
    page_2 = sub_2.add_page("Page 2")
    assert page_1.previous_page is None
    assert page_1.next_page is page_2
    assert page_2.previous_page is page_1
    assert page_2.next_page is None
    page_3 = nav.add_page("Page 3")
    assert page_2.next_page is page_3
    assert page_3.previous_page is page_2


EXPECTED = """---
description: Some description
hide:
- toc
- path
icon: material/emoticon-happy
search:
  boost: 2.0
  exclude: false
status: new
subtitle: Some subtitle
title: Some title
---

"""


def test_metadata():
    page = mk.MkPage(
        hide="toc,path",
        search_boost=2.0,
        exclude_from_search=False,
        icon="material/emoticon-happy",
        status="new",
        title="Some title",
        subtitle="Some subtitle",
        description="Some description",
    )
    page.metadata.pop("created")
    assert str(page) == EXPECTED

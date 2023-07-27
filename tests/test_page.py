from __future__ import annotations

import mknodes


def test_page():
    page = mknodes.MkPage()
    assert not str(page)


EXPECTED = """---
description: Some description
hide:
- toc
- navigation
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
    page = mknodes.MkPage(
        hide_toc=True,
        hide_nav=False,
        hide_path=True,
        search_boost=2.0,
        exclude_from_search=False,
        icon="material/emoticon-happy",
        status="new",
        title="Some title",
        subtitle="Some subtitle",
        description="Some description",
    )
    assert str(page) == EXPECTED

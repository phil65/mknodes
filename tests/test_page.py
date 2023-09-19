from __future__ import annotations

import mknodes


def test_page():
    page = mknodes.MkPage()
    page._metadata.pop("created")
    assert not str(page)


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
    page = mknodes.MkPage(
        hide="toc,path",
        search_boost=2.0,
        exclude_from_search=False,
        icon="material/emoticon-happy",
        status="new",
        title="Some title",
        subtitle="Some subtitle",
        description="Some description",
    )
    page._metadata.pop("created")
    assert str(page) == EXPECTED

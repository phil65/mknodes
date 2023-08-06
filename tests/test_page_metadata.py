from __future__ import annotations

from mknodes.pages import metadata


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

example_metadata = metadata.Metadata(
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


def test_metadata():
    assert str(example_metadata) == EXPECTED


def test_parsing_metadata():
    parsed, _rest = metadata.Metadata.parse(EXPECTED)
    assert str(parsed) == EXPECTED

from __future__ import annotations

import mknodes as mk


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

example_metadata = mk.Metadata(
    hide=["toc", "path"],
    search_boost=2.0,
    exclude_from_search=False,
    icon="material/emoticon-happy",
    status="new",
    title="Some title",
    subtitle="Some subtitle",
    description="Some description",
)


def test_metadata():
    assert example_metadata.as_page_header() == EXPECTED


def test_no_string_if_empty():
    data = mk.Metadata()
    assert not data.as_page_header()


def test_parsing_metadata():
    parsed, _rest = mk.Metadata.parse(EXPECTED)
    assert parsed.as_page_header() == EXPECTED


def test_metadata_inheritance():
    nav = mk.MkNav()
    nav.metadata["test"] = "Test"
    page = nav.add_page("Test")
    page.metadata["test_2"] = "Test 2"
    assert page.resolved_metadata["test"] == "Test"
    assert page.resolved_metadata["test_2"] == "Test 2"


def test_overwriting_inherited_metadata():
    nav = mk.MkNav()
    nav.metadata["test"] = "Test"
    page = nav.add_page("Test")
    page.metadata["test"] = "Test 2"
    assert page.resolved_metadata["test"] == "Test 2"

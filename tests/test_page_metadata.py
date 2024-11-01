from __future__ import annotations

import pytest

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
    """Test the metadata functionality.
    
    This method verifies that the `as_page_header()` method of the `example_metadata` object
    returns the expected value defined in the `EXPECTED` constant.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the output of `example_metadata.as_page_header()` does not match
                        the `EXPECTED` constant.
    """
    assert example_metadata.as_page_header() == EXPECTED


def test_no_string_if_empty():
    """Test if an empty Metadata object returns an empty string as page header
    
    Args:
        None
    
    Returns:
        None: This test method doesn't return a value, it uses assertions
    
    Raises:
        AssertionError: If data.as_page_header() returns a non-empty string
    """
    data = mk.Metadata()
    assert not data.as_page_header()


def test_parsing_metadata():
    """Test the parsing of metadata.
    
    Args:
        None
    
    Returns:
        None: This test function doesn't return anything explicitly.
    
    Raises:
        AssertionError: If the parsed metadata does not match the expected output.
    """
    parsed, _rest = mk.Metadata.parse(EXPECTED)
    assert parsed.as_page_header() == EXPECTED


def test_metadata_inheritance():
    """Tests the inheritance of metadata in the navigation structure.
    
    This method creates a navigation object, sets metadata on it, adds a page
    to the navigation, sets additional metadata on the page, and then asserts
    that the metadata is correctly inherited and resolved.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the metadata is not correctly inherited or resolved.
    """
    nav = mk.MkNav()
    nav.metadata["test"] = "Test"
    page = nav.add_page("Test")
    page.metadata["test_2"] = "Test 2"
    assert page.resolved_metadata["test"] == "Test"
    assert page.resolved_metadata["test_2"] == "Test 2"


def test_overwriting_inherited_metadata():
    """Test overwriting of inherited metadata in a navigation structure.
    
    This method creates a navigation structure with a page, sets metadata at both
    the navigation and page levels, and verifies that page-level metadata
    overwrites navigation-level metadata when resolved.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the page's resolved metadata does not match the expected value.
    """
    nav = mk.MkNav()
    nav.metadata["test"] = "Test"
    page = nav.add_page("Test")
    page.metadata["test"] = "Test 2"
    assert page.resolved_metadata["test"] == "Test 2"


if __name__ == "__main__":
    pytest.main([__file__])

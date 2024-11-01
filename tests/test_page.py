from __future__ import annotations

import pytest

import mknodes as mk


def test_page():
    """Test the initialization of an empty MkPage object.
    
    This method creates a new MkPage object, removes the 'created' metadata,
    and asserts that the string representation of the page is empty.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the page is not empty
                        after removing the 'created' metadata.
    """
    page = mk.MkPage()
    page.metadata.pop("created")
    assert not str(page)


def test_next_and_previous_page():
    """Tests the navigation between pages using next_page and previous_page attributes.
    
    This method creates a navigation object and two pages, then asserts the correct
    linking between the pages using their next_page and previous_page attributes.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If any of the navigation assertions fail.
    """
    nav = mk.MkNav()
    page_1 = nav.add_page("Page 1")
    page_2 = nav.add_page("Page 2")
    assert page_1.previous_page is None
    assert page_1.next_page is page_2
    assert page_2.previous_page is page_1
    assert page_2.next_page is None


def test_next_and_previous_page_across_navs():
    """Test navigation between pages across different navigation sections.
    
    This method creates a navigation structure with multiple sections and pages,
    then tests the functionality of next_page and previous_page attributes
    across different navigation sections.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If any of the navigation links are incorrect
    """
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
    """Tests the metadata functionality of the MkPage class.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the metadata as page header does not match the expected value.
    
    This method creates an MkPage object with specific metadata attributes, removes the 'created' attribute,
    and then asserts that the page header generated from the metadata matches an expected value (EXPECTED).
    The test verifies the correct handling and formatting of metadata in the MkPage class.
    """
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
    assert page.metadata.as_page_header() == EXPECTED


if __name__ == "__main__":
    pytest.main([__file__])

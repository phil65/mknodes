from __future__ import annotations

import pytest

import mknodes as mk


TREE_NUM_PAGES = 5
TREE_NUM_NAVS = 3
TREE_NUM_TEXT = 5
TREE_TOTAL = TREE_NUM_PAGES + TREE_NUM_NAVS + TREE_NUM_TEXT


def test_nav():
    """Create and configure a MkNav object for navigation.
    
    This method demonstrates the creation and configuration of a MkNav object,
    which is likely part of a documentation or website generation system.
    It adds documents, pages, and a sub-navigation item to the navigation structure.
    
    Args:
        None
    
    Returns:
        None: This method doesn't return a value, it performs actions on a MkNav object.
    
    Raises:
        Possible exceptions are not explicitly handled or documented in this method.
    """
    nav = mk.MkNav()
    nav.add_doc(mk)
    nav.add_page("Test")
    nav.add_page("Test Index page", is_index=True)
    nav.add_nav("sub")


def test_from_folder(test_data_dir):
    """Tests the parsing of a folder structure for navigation tree creation.
    
    Args:
        test_data_dir (Path): The directory containing the test data for navigation tree.
    
    Returns:
        None: This method doesn't return anything, it uses assertions for testing.
    
    Raises:
        AssertionError: If the number of descendants in the parsed navigation tree
                        doesn't match the expected total (TREE_TOTAL - 1).
    """
    nav = mk.MkNav()
    nav.parse.folder(test_data_dir / "nav_tree")
    assert len(list(nav.descendants)) == TREE_TOTAL - 1


def test_from_file(test_data_dir):
    """Test the creation of a navigation tree from a file.
    
    Args:
        test_data_dir (Path): Directory containing test data files.
    
    Returns:
        None
    
    Raises:
        AssertionError: If the number of descendants in the navigation tree
            does not match the expected total (TREE_TOTAL - 1).
    """
    nav_file = test_data_dir / "nav_tree/SUMMARY.md"
    nav = mk.MkNav()
    nav.parse.file(nav_file)
    assert len(list(nav.descendants)) == TREE_TOTAL - 1


def test_resolved_path():
    """Test the resolved path of a nested navigation structure.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the resolved_parts of the subsubnav do not match the expected value.
    """
    nav = mk.MkNav()
    subnav = nav.add_nav("subsection")
    subsubnav = subnav.add_nav("subsubsection")
    assert subsubnav.resolved_parts == ("subsection", "subsubsection")


def test_creating_module_document():
    """Tests the creation of a module document in the navigation structure.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the created module_docs object has no children.
    """
    nav = mk.MkNav()
    subnav = nav.add_nav("subsection")
    module_docs = subnav.add_doc(pytest)
    assert module_docs.children


if __name__ == "__main__":
    pytest.main([__file__])

from __future__ import annotations

import pytest

import mknodes as mk


def test_empty():
    """Test an empty MkText node.
    
    This method creates an empty MkText node and asserts that its string representation is empty.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the empty MkText node is not empty.
    """
    node = mk.MkText()
    assert not str(node)


def test_getitem_ending_with_eof():
    """Test the __getitem__ method for a MkText node with content ending at EOF
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the __getitem__ method does not correctly extract the content
                        following the specified section header up to the end of the file.
    """
    node = mk.MkText("## Test section\nTest")
    assert str(node["Test section"]) == "Test"


def test_getitem_ending_with_another_section():
    """
    Test the __getitem__ method for a section ending with another section
    
    This method tests the behavior of the __getitem__ method when accessing a section
    that is immediately followed by another section in a MkText object.
    
    Args:
        None
    
    Returns:
        None: This test method doesn't return a value, it uses assertions to verify behavior
    
    Raises:
        AssertionError: If the extracted content doesn't match the expected string
    """
    node = mk.MkText("## Test section\nTest\n## Another section")
    assert str(node["Test section"]) == "Test\n"


def test_fetch_from_url():
    """Fetches content from a GitHub URL and creates a MkText node.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the created MkText node cannot be converted to a string.
    """
    url = "https://raw.githubusercontent.com/fire1ce/DDNS-Cloudflare-Bash/main/README.md"
    node = mk.MkText.from_url(url)
    assert str(node)


def test_rendered_children():
    """Tests the rendering of nested children in MkText nodes.
    
    This method verifies the correct behavior of rendering nested Jinja templates
    within MkText nodes, particularly focusing on the creation and hierarchy of
    child nodes when using the MkAdmonition filter.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If any of the assertions about the node structure,
                        hierarchy, or number of descendants fail.
    """
    node = mk.MkText("{{ 'Test' | MkAdmonition | MkAdmonition }}", render_jinja=True)
    num_desc = 3  # 2 * MkAdmonition, 1 * MkText
    assert len(node.children) == 1
    assert len(list(node.descendants)) == num_desc
    admon_inner = node.children[0]
    text_inner = admon_inner.children[0]
    assert admon_inner == text_inner.parent
    assert node == admon_inner.parent
    assert node.parent is None

    node = mk.MkText("{{ mk.MkAdmonition(mk.MkAdmonition('test')) }}", render_jinja=True)
    assert len(node.children) == 1
    assert len(list(node.descendants)) == num_desc
    admon_inner = node.children[0]
    text_inner = admon_inner.children[0]
    assert admon_inner == text_inner.parent
    assert node == admon_inner.parent
    assert node.parent is None


if __name__ == "__main__":
    pytest.main([__file__])

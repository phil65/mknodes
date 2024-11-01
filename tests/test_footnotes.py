from __future__ import annotations

import pytest

import mknodes as mk


EXPECTED = """## Header

[^1]:
    abcde
    fghi
[^2]:
    abcde
    fghi
[^3]:
    abcde
    fghi
[^4]:
    abcde
    fghi
[^5]:
    abcde
    fghi
[^6]:
    abcde
    fghi
[^7]:
    abcde
    fghi
[^8]:
    abcde
    fghi
[^9]:
    abcde
    fghi
[^10]:
    abcde
    fghi
"""

EXPECTED_SORTED = """[^1]:
    1
[^2]:
    2
"""


def test_empty():
    """Test if an empty MkFootNotes object produces an empty string representation.
    
    Args:
        None
    
    Returns:
        None: This test method doesn't return a value, it uses assertions.
    
    Raises:
        AssertionError: If the string representation of an empty MkFootNotes object is not empty.
    """
    annotation = mk.MkFootNotes()
    assert not str(annotation)


def test_if_annotations_get_sorted():
    """Tests if annotations in MkFootNotes are sorted correctly.
    
    This method creates an instance of MkFootNotes, adds footnotes with
    out-of-order keys, and checks if the string representation is sorted
    as expected.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the MkFootNotes
                        instance does not match the expected sorted output.
    """
    node = mk.MkFootNotes()
    node[2] = "2"
    node[1] = "1"
    assert str(node) == EXPECTED_SORTED


def test_markdown():
    """Test the markdown footnotes functionality.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the MkFootNotes object
                        does not match the expected output.
    """
    annotation = mk.MkFootNotes(["abcde\nfghi"] * 10, header="Header")
    assert str(annotation) == EXPECTED


def test_constructors():
    """Tests the constructors of the MkFootNotes class.
    
    This method creates two MkFootNotes objects using different constructor
    approaches and asserts that their string representations are equal.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representations of the two MkFootNotes
                        objects are not equal.
    """
    annotation_1 = mk.MkFootNotes(["abc", "def"])
    anns = {1: "abc", 2: "def"}
    annotation_2 = mk.MkFootNotes(anns)
    assert str(annotation_1) == str(annotation_2)


def test_mapping_interface():
    """Tests the mapping interface of the MkFootNotes class.
    
    This method creates an instance of MkFootNotes, assigns a value to a key,
    and asserts that the string representation of the assigned value matches
    the expected format for a footnote.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the assigned footnote
                        does not match the expected format.
    """
    ann = mk.MkFootNotes()
    ann[1] = "test"
    assert str(ann[1]) == "[^1]:\n    test\n"


if __name__ == "__main__":
    pytest.main([__file__])

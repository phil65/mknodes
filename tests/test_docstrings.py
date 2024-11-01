from __future__ import annotations

import pytest

import mknodes as mk


EXPECTED_IN_ANNOTATIONS = """\
1.  ::: mknodes.basenodes._mkdocstrings.MkDocStrings.__init__
        options:
          docstring_section_style: 'list'
          show_root_heading: True

"""


def test_docstrings():
    """Test the generation of docstrings for the MkDocStrings class.
    
    This method creates an instance of MkDocStrings with the 'mk' object and checks
    if the string representation of the docstrings matches the expected output.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the generated docstring does not match the expected string.
    """
    docstrings = mk.MkDocStrings(obj=mk)
    assert str(docstrings) == "::: mknodes\n"


def test_auto_list_style_inside_annotations():
    """Tests the auto list style functionality inside annotations.
    
    Args:
        None
    
    Returns:
        None: This method doesn't return anything explicitly.
    
    Raises:
        AssertionError: If the string representation of annotations does not match the expected value.
    """
    annotations = mk.MkAnnotations()
    annotations[1] = mk.MkDocStrings(obj=mk.MkDocStrings.__init__)
    assert str(annotations) == EXPECTED_IN_ANNOTATIONS


if __name__ == "__main__":
    pytest.main([__file__])

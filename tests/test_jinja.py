from __future__ import annotations

import pytest

import mknodes as mk


def test_if_mknodes_parent_is_set():
    """Tests if the parent of MkNodes is correctly set when rendered.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the parent of the rendered node is not set to the page.
    """
    page = mk.MkPage()
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert page.env.rendered_nodes[-1].parent == page


def test_correct_child_count_after_multiple_renders():
    """Test correct child count after multiple renders
    
    This method tests the behavior of rendering multiple MkHeader nodes and ensures that the rendered_nodes count remains correct after multiple render operations.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the number of rendered nodes is not as expected after rendering operations
    """
    page = mk.MkPage()
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert len(page.env.rendered_nodes) == 1
    page.env.render_string(r"{{ 'test' | MkHeader }}")
    assert len(page.env.rendered_nodes) == 1
    env = page.env
    env.render_string(r"{{ 'test' | MkHeader }}")
    env.render_string(r"{{ 'test' | MkHeader }}")
    assert len(env.rendered_nodes) == 1


if __name__ == "__main__":
    pytest.main([__file__])

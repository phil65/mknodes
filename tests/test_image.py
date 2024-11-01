from __future__ import annotations

import pytest

import mknodes as mk


EXPECTED = """<figure markdown>
  ![Image title](something.png)
  <figcaption>Caption</figcaption>
</figure>
"""


def test_image():
    """Test the creation and string representation of an MkImage object.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the string representation of the MkImage object does not match the expected value.
    """
    image = mk.MkImage(path="something.png", caption="Caption", title="Image title")
    assert str(image) == EXPECTED


if __name__ == "__main__":
    pytest.main([__file__])

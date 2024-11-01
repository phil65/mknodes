import pytest

from mknodes.utils.color import Color


def test_color_init_with_str():
    color = Color("red")
    assert color.space() == "srgb"
    assert color.alpha() == 1.0


def test_color_init_with_rgb_tuple():
    """Test the initialization of a Color object with an RGB tuple.
    
    This method tests the creation of a Color object using an RGB tuple (255, 0, 0),
    which represents pure red. It verifies that the resulting color has the correct
    color space ('srgb') and alpha value (1.0).
    
    Args:
        None
    
    Returns:
        None: This test method doesn't return a value, but uses assertions to
        verify the correctness of the Color object initialization.
    
    Raises:
        AssertionError: If the color space is not 'srgb' or if the alpha value
        is not 1.0.
    """
    color = Color((255, 0, 0))
    assert color.space() == "srgb"
    assert color.alpha() == 1.0


def test_color_init_with_rgba_tuple():
    """Tests the initialization of a Color object with an RGBA tuple.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the color space is not 'srgb' or if the alpha value is not 0.5.
    """
    color = Color((255, 0, 0, 0.5))
    assert color.space() == "srgb"
    assert color.alpha() == 0.5  # noqa: PLR2004


def test_color_init_with_invalid_type():
    """Test initialization of Color with an invalid type.
    
    This method tests that a TypeError is raised when attempting to initialize a Color object with an invalid type (in this case, an integer).
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        pytest.raises(TypeError): Ensures that a TypeError is raised when initializing Color with an integer.
    """
    with pytest.raises(TypeError):
        Color(123)  # type: ignore[arg-type]


def test_color_str():
    """Test the string representation of a Color object.
    
    This method creates a Color object with the color "red" and verifies that its
    string representation matches the expected RGB format.
    
    Returns:
        None: This test method doesn't return a value, but raises an AssertionError
        if the test fails.
    
    Raises:
        AssertionError: If the string representation of the Color object does not
        match the expected RGB format.
    """
    color = Color("red")
    assert str(color) == "rgb(255, 0, 0)"


def test_color_brightness():
    """Test the brightness adjustment of a Color object.
    
    This method creates a red Color object, increases its brightness,
    and asserts that the resulting color has a higher luminance.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the brightened color's luminance is not greater
                        than the original color's luminance.
    """
    color = Color("red")
    brighter_color = color.brightness(1.5)
    assert brighter_color.luminance() > color.luminance()


def test_color_set_alpha():
    """Tests the set_alpha method of the Color class.
    
    Args:
        None
    
    Returns:
        None
    
    Raises:
        AssertionError: If the alpha value is not set correctly.
    """
    color = Color("red")
    color.set_alpha(0.5)
    assert color.alpha() == 0.5  # noqa: PLR2004


if __name__ == "__main__":
    pytest.main([__file__])

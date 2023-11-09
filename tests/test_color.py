import pytest

from mknodes.utils.color import Color


def test_color_init_with_str():
    color = Color("red")
    assert color.space() == "srgb"
    assert color.alpha() == 1.0  # noqa: PLR2004


def test_color_init_with_rgb_tuple():
    color = Color((255, 0, 0))
    assert color.space() == "srgb"
    assert color.alpha() == 1.0  # noqa: PLR2004


def test_color_init_with_rgba_tuple():
    color = Color((255, 0, 0, 0.5))
    assert color.space() == "srgb"
    assert color.alpha() == 0.5  # noqa: PLR2004


def test_color_init_with_invalid_type():
    with pytest.raises(TypeError):
        Color(123)


def test_color_str():
    color = Color("red")
    assert str(color) == "rgb(255, 0, 0)"


def test_color_brightness():
    color = Color("red")
    brighter_color = color.brightness(1.5)
    assert brighter_color.luminance() > color.luminance()


def test_color_set_alpha():
    color = Color("red")
    color.set_alpha(0.5)
    assert color.alpha() == 0.5  # noqa: PLR2004

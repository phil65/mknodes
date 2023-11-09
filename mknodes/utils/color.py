from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import coloraide


RGB_TUPLE_LEN = 3
ALPHA_DEFAULT = 1.0


class Color(coloraide.Color):
    def __init__(
        self,
        color: str | tuple,
        data: Sequence[float] | None = None,
        alpha: float = ALPHA_DEFAULT,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            color: Color, either as string or (a)rgb tuple
            data: Optional data in case color is a str (see ColorAide docs)
            alpha: Alpha value for the color (0 - 1)
            kwargs: Optional keyword arguments passed to parent
        """
        match color:
            case str():
                super().__init__(color, data=data, alpha=alpha, **kwargs)
                if not data and alpha != ALPHA_DEFAULT:
                    self["alpha"] = alpha
            case tuple() if len(color) == RGB_TUPLE_LEN:
                super().__init__("srgb", [i / 255 for i in color], alpha=alpha, **kwargs)
            case tuple():
                super().__init__("srgb", [i / 255 for i in color[:3]], color[3], **kwargs)
            case _:
                raise TypeError(color)

    def __str__(self):
        """Return str in form of rgb(255, 0, 0)."""
        return self.to_string(comma=True)

    def brightness(self, value: float, **kwargs: Any):
        """Change brightness of given color.

        Arguments:
            value: The new brightness
            kwargs: Keyword arguments passed to parent
        """
        return self.filter("brightness", value, **kwargs)

    def set_alpha(self, value: float):
        """Change the color alpha value.

        Arguments:
            value: The new alpha value
        """
        self["alpha"] = value


if __name__ == "__main__":
    color = Color("red", alpha=0.5)
    print(color)

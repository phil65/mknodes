from __future__ import annotations

import coloraide


rgb_tuple_len = 3
ALPHA_DEFAULT = 1.0


class Color(coloraide.Color):
    def __init__(
        self,
        color: str | tuple,
        data=None,
        alpha: float = ALPHA_DEFAULT,
        **kwargs,
    ):
        match color:
            case str():
                super().__init__(color, data=data, alpha=alpha, **kwargs)
                if not data and alpha != ALPHA_DEFAULT:
                    self["alpha"] = alpha
            case tuple() if len(color) == rgb_tuple_len:
                super().__init__("srgb", [i / 255 for i in color], alpha=alpha, **kwargs)
            case tuple():
                super().__init__("srgb", [i / 255 for i in color[:3]], color[3], **kwargs)
            case _:
                raise TypeError(color)

    def __str__(self):
        """Return str in form of rgb(255, 0, 0)."""
        return self.to_string(comma=True)

    def brightness(self, value: float, **kwargs):
        return self.filter("brightness", value, **kwargs)

    def set_alpha(self, value: float):
        color["alpha"] = value


if __name__ == "__main__":
    color = Color("red", alpha=0.5)
    print(color)

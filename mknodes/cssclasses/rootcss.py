from __future__ import annotations

from mknodes.cssclasses import cssclasses


RGB_TUPLE_LEN = 3


class RootCSS(cssclasses.CSS):
    PREFIX = ":root"

    def __init__(self):
        super().__init__(r":root {}")


# if __name__ == "__main__":
#     ss = RootCSS()
#     ss.set_primary_background_color((100, 100, 100))
#     print(ss)

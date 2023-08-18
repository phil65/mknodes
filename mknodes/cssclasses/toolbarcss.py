from __future__ import annotations

from mknodes.cssclasses import cssclasses


TOOLTIP = """
:root {
  --md-tooltip-width: 700px;
  --md-tooltip-width: 700px;
}
"""


class ToolbarCss(cssclasses.CSS):
    def __init__(self):
        super().__init__(TOOLTIP)

    def set_height(self, width: int):
        width = width


if __name__ == "__main__":
    ss = ToolbarCss()
    print(ss[0].selector)

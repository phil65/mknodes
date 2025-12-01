from __future__ import annotations

import dataclasses


# from typing import Literal


@dataclasses.dataclass(frozen=True)
class AdmonitionType:
    name: str
    svg: str
    header_color: str
    icon_color: str
    border_color: str
    font_color: str

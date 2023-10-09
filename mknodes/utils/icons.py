from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from xml.etree import ElementTree as et


def get_material_icon_path(icon: str) -> pathlib.Path:
    import material

    if "/" not in icon:
        icon = f"material/{icon}"
    path = pathlib.Path(next(iter(material.__path__)))
    return path / "templates" / ".icons" / f"{icon}.svg"


def get_icon_svg(icon: str) -> str:
    if icon.startswith(":") or ":" not in icon:
        path = get_material_icon_path(icon)
        return path.read_text()
    import pyconify

    return pyconify.svg(icon).decode()


def get_icon_xml(icon: str) -> et.Element:
    """Return a xmlElement for given MaterialIcon.

    Arguments:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    from xml.etree import ElementTree as et

    et.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = get_icon_svg(icon)
    return et.fromstring(svg_text)


if __name__ == "__main__":
    print(get_icon_svg("mdi:wrench"))

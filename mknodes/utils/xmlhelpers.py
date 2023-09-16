from __future__ import annotations

from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


def get_material_icon_svg(icon: str):
    """Return a xmlElement for given MaterialIcon.

    Arguments:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    from xml.etree import ElementTree

    if "/" not in icon:
        icon = f"material/{icon}"
    path = pathhelpers.get_material_icon_path(icon)
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = path.read_text()
    return ElementTree.fromstring(svg_text)


def pformat(str_or_elem, space: str = "  ", level: int = 0):
    """Prettyprint given XML.

    Arguments:
        str_or_elem: XML to prettyprint
        space: Amount of spaces to use for indentation
        level: Initial indentation level
    """
    from xml.etree import ElementTree

    if isinstance(str_or_elem, str):
        str_or_elem = ElementTree.fromstring(str_or_elem)
    ElementTree.indent(str_or_elem, space=space, level=level)
    return ElementTree.tostring(str_or_elem, encoding="unicode")


if __name__ == "__main__":
    text = pformat("<a>fjkj</a>")
    print(text)

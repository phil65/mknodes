from __future__ import annotations

from xml.etree import ElementTree as Et

from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


class Div(Et.Element):
    def __init__(self, klass: str | None = None, parent=None, **kwargs):
        attrs = {"class": klass} if klass else {}
        super().__init__("div", attrs | kwargs)
        if parent is not None:
            parent.append(self)


def get_material_icon_svg(icon: str):
    """Return a xmlElement for given MaterialIcon.

    Arguments:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    path = pathhelpers.get_material_icon_path(icon)
    Et.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = path.read_text()
    return Et.fromstring(svg_text)


def pformat(str_or_elem, space: str = "  ", level: int = 0):
    """Prettyprint given XML.

    Arguments:
        str_or_elem: XML to prettyprint
        space: Amount of spaces to use for indentation
        level: Initial indentation level
    """
    if isinstance(str_or_elem, str):
        str_or_elem = Et.fromstring(str_or_elem)
    Et.indent(str_or_elem, space=space, level=level)
    return Et.tostring(str_or_elem, encoding="unicode")


if __name__ == "__main__":
    a = Div("test")

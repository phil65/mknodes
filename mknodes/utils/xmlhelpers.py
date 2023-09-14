from __future__ import annotations

from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


def get_material_icon_svg(icon: str):
    from xml.etree import ElementTree

    path = pathhelpers.get_material_icon_path(icon)
    ElementTree.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = path.read_text()
    return ElementTree.fromstring(svg_text)


def pformat(str_or_elem):
    from xml.dom import minidom
    from xml.etree import ElementTree

    if isinstance(str_or_elem, ElementTree.Element):
        str_or_elem = ElementTree.tostring(str_or_elem)
    return minidom.parseString(str_or_elem).childNodes[0].toprettyxml(indent="  ")


if __name__ == "__main__":
    text = pformat("<a>fjkj</a>")
    print(text)

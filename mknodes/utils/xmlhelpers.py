from __future__ import annotations

from xml.etree import ElementTree as Et

from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


class HTMLElement(Et.Element):
    def to_string(self, space: str = "  ", level: int = 0) -> str:
        Et.indent(self, space=space, level=level)
        return Et.tostring(self, encoding="unicode", method="html")


class Div(HTMLElement):
    def __init__(
        self,
        klass: str | None = None,
        text: str | None = None,
        parent: Et.Element | None = None,
        **kwargs,
    ):
        attrs = {"class": klass} if klass else {}
        super().__init__("div", attrs | kwargs)
        self.text = text
        if parent is not None:
            parent.append(self)


class Header(HTMLElement):
    def __init__(self, level: int, text: str, parent=None, **kwargs):
        super().__init__(f"h{level}", kwargs)
        self.text = text
        if parent is not None:
            parent.append(self)


class P(HTMLElement):
    def __init__(self, klass: str | None = None, parent=None, **kwargs):
        attrs = {"class": klass} if klass else {}
        super().__init__("p", attrs | kwargs)
        if parent is not None:
            parent.append(self)


class Section(HTMLElement):
    def __init__(self, klass: str | None = None, parent=None, **kwargs):
        attrs = {"class": klass} if klass else {}
        super().__init__("section", attrs | kwargs)
        if parent is not None:
            parent.append(self)


class Img(HTMLElement):
    def __init__(self, klass: str | None = None, parent=None, **kwargs):
        attrs = {"class": klass} if klass else {}
        super().__init__("img", attrs | kwargs)
        if parent is not None:
            parent.append(self)


class A(HTMLElement):
    def __init__(
        self,
        klass: str | None = None,
        text: str | None = None,
        parent=None,
        **kwargs,
    ):
        attrs = {"class": klass} if klass else {}
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        super().__init__("a", attrs | kwargs)
        self.text = text
        if parent is not None:
            parent.append(self)


def get_material_icon_svg(icon: str) -> Et.Element:
    """Return a xmlElement for given MaterialIcon.

    Arguments:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    path = pathhelpers.get_material_icon_path(icon)
    Et.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = path.read_text()
    return Et.fromstring(svg_text)


def pformat(str_or_elem: str | Et.Element, space: str = "  ", level: int = 0) -> str:
    """Prettyprint given XML.

    Arguments:
        str_or_elem: XML to prettyprint
        space: Amount of spaces to use for indentation
        level: Initial indentation level
    """
    if isinstance(str_or_elem, str):
        str_or_elem = Et.fromstring(str_or_elem)
    Et.indent(str_or_elem, space=space, level=level)
    return Et.tostring(str_or_elem, encoding="unicode", method="html")


if __name__ == "__main__":
    a = Div("test")

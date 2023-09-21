from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as Et

from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


class HTMLElement(Et.Element):
    tag_name: str

    def __init__(
        self,
        klass: str | None = None,
        parent: Et.Element | None = None,
        **kwargs: Any,
    ):
        attrs = {"class": klass} if klass else {}
        super().__init__(self.tag_name, attrs | kwargs)
        if parent is not None:
            parent.append(self)

    def to_string(self, space: str = "  ", level: int = 0) -> str:
        Et.indent(self, space=space, level=level)
        return Et.tostring(self, encoding="unicode", method="html")


class Div(HTMLElement):
    tag_name = "div"

    def __init__(
        self,
        klass: str | None = None,
        text: str | None = None,
        parent: Et.Element | None = None,
        **kwargs: Any,
    ):
        super().__init__(klass, parent, **kwargs)
        self.text = text


class Header(HTMLElement):
    def __init__(
        self,
        level: int,
        text: str,
        parent: Et.Element | None = None,
        **kwargs: Any,
    ):
        self.tag_name = f"h{level}"
        super().__init__(**kwargs)
        self.text = text
        if parent is not None:
            parent.append(self)


class P(HTMLElement):
    tag_name = "p"


class Section(HTMLElement):
    tag_name = "section"


class Img(HTMLElement):
    tag_name = "img"


class Ul(HTMLElement):
    tag_name = "ul"


class Li(HTMLElement):
    tag_name = "li"


class Button(HTMLElement):
    tag_name = "button"


class Form(HTMLElement):
    tag_name = "form"


class Input(HTMLElement):
    tag_name = "input"


class Label(HTMLElement):
    tag_name = "label"


class A(HTMLElement):
    tag_name = "a"

    def __init__(
        self,
        klass: str | None = None,
        text: str | None = None,
        parent: Et.Element | None = None,
        **kwargs: Any,
    ):
        super().__init__(klass, parent, **kwargs)
        self.text = text


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


def get_source_button(icon: str = "material/code-json"):
    href = (
        "{{ config.site_url | rstrip('/') + '/src/' + page.file.src_uri | replace('.md',"
        " '.original') }}"
    )
    elem = A(
        "md-content__button md-icon",
        title="Source",
        href=href,
    )
    elem.append(get_material_icon_svg(icon))
    return elem


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

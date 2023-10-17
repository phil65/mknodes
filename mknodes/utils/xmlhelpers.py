from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as Et

from mknodes.utils import icons, log


logger = log.get_logger(__name__)


class HTMLElement(Et.Element):
    tag_name: str

    def __init__(
        self,
        klass: str | None = None,
        parent: Et.Element | None = None,
        *,
        attrs: dict | None = None,
        markdown: bool = False,
        **kwargs: str,
    ):
        """Constructor.

        Arguments:
            klass: CSS class
            parent: Optional parent element
            attrs: A dict containing XML attributes
            markdown: Set markdown attribute. (Also sets markdown attr for parents)
            kwargs: Additional XML attributes
        """
        kls = {"class": klass} if klass else {}
        self.parent = parent
        attrs = attrs or {}
        super().__init__(self.tag_name, attrs | kwargs | kls)
        if parent is not None:
            parent.append(self)
        if markdown:
            node = self
            while node is not None:
                node.set("markdown", "1")
                if isinstance(node, HTMLElement) and node.parent:
                    node = node.parent
                else:
                    break

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


class Span(HTMLElement):
    tag_name = "span"

    def __init__(
        self,
        klass: str | None = None,
        text: str | None = None,
        parent: Et.Element | None = None,
        **kwargs: Any,
    ):
        super().__init__(klass, parent, **kwargs)
        self.text = text


class Img(HTMLElement):
    tag_name = "img"


class Ul(HTMLElement):
    tag_name = "ul"


class Li(HTMLElement):
    tag_name = "li"


class Table(HTMLElement):
    tag_name = "table"


class Tr(HTMLElement):
    tag_name = "tr"


class Aside(HTMLElement):
    tag_name = "aside"


class Td(HTMLElement):
    tag_name = "td"


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


def get_source_button(icon: str = "material/code-json") -> A:
    href = (
        "{{ config.site_url | rstrip('/') + '/src/' + page.file.src_uri | replace('.md',"
        " '.original') }}"
    )
    elem = A(
        "md-content__button md-icon",
        title="Source",
        href=href,
    )
    svg = icons.get_icon_xml(icon)
    elem.append(svg)
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

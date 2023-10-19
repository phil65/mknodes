from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers, resources, xmlhelpers as xml


logger = log.get_logger(__name__)


class MkMaterialBadge(mknode.MkNode):
    """Node for a CSS-based badge a la MkDocs-Material."""

    ICON = "simple/shieldsdotio"
    CSS = [resources.CSSFile("css/materialbadge.css")]

    def __init__(
        self,
        icon: str,
        text: str = "",
        typ: Literal["heart", "right", ""] = "",
        link: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            icon: Icon to display
            text: Text to display
            typ: Optional badge type
            link: Optional URL to link to
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.icon = icon
        self.text = text
        self.typ = typ
        self.link = link

    def _to_markdown(self):
        classes = (
            f"md-typeset mdx-badge mdx-badge--{self.typ}"
            if self.typ
            else "mdx-badge md-typeset"
        )
        root = xml.Span(classes)
        if self.icon:
            xml.Span("mdx-badge__icon", parent=root, text=self.icon)
        if self.text:
            xml.Span("mdx-badge__text", parent=root, text=self.text)
        return root.to_string()

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            icon=self.icon,
            text=self.text,
            typ=self.typ,
            link=self.link,
            _filter_empty=True,
        )

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkMaterialBadge(icon=":material-file:", text="text")
        page += mk.MkReprRawRendered(node)

        node = MkMaterialBadge(icon=":material-file:", text="text", typ="heart")
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    img = MkMaterialBadge("Left", "right")
    print(img)

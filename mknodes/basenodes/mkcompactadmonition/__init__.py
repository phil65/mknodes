from __future__ import annotations

from typing import Any, get_args

from mknodes.basenodes import mknode
from mknodes.data import datatypes
from mknodes.utils import log, resources, xmlhelpers


logger = log.get_logger(__name__)


class MkCompactAdmonition(mknode.MkNode):
    """Compact admonition info box."""

    ICON = "octicons/info-16"
    CSS = [resources.CSSFile("compactadmonition.css")]

    def __init__(
        self,
        text: str | mknode.MkNode,
        *,
        typ: datatypes.AdmonitionTypeStr | str = "info",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Admonition text
            typ: Admonition type
            kwargs: Keyword arguments passed to parent
        """
        self.text = text
        self.typ = typ
        super().__init__(**kwargs)

    def _to_markdown(self) -> str:
        kls = f"mdx-grid-wrapper mdx-admo--{self.typ}" if self.typ else "mdx-grid-wrapper"
        root = xmlhelpers.Div(kls)
        xmlhelpers.Div("mdx-grid-child mdx-grid-child--icon", parent=root)
        text_div = xmlhelpers.Div("mdx-grid-child", parent=root)
        text_div.text = str(self.text)
        return root.to_string()

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        for typ in get_args(datatypes.AdmonitionTypeStr):
            page += mk.MkHeader(f"Type '{typ}'", level=3)
            content = f"This is type **{typ}**"
            node = MkCompactAdmonition(typ=typ, text=content)
            page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    admonition = MkCompactAdmonition("FDSFDFSFS", typ="bug")
    print(admonition)

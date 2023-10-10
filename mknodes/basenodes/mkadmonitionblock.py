from __future__ import annotations

from typing import Any, get_args

from mknodes.basenodes import mkblock, mknode
from mknodes.data import datatypes
from mknodes.utils import log, reprhelpers, resources


logger = log.get_logger(__name__)


class MkAdmonitionBlock(mkblock.MkBlock):
    """Pymdownx-based Admonition Block."""

    ICON = "octicons/info-16"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.blocks.admonition")]

    def __init__(
        self,
        content: str | list | mknode.MkNode,
        *,
        typ: datatypes.AdmonitionTypeStr = "info",
        title: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Admonition content
            typ: Admonition type
            title: Optional Admonition title
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            "admonition",
            content=content,
            argument=title or "",
            attributes=dict(type=typ),
            **kwargs,
        )
        self.typ = typ
        self.title = title

    def __repr__(self):
        if len(self.items) == 1:
            content = reprhelpers.to_str_if_textnode(self.items[0])
        else:
            content = [reprhelpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(self, content=content, typ=self.typ, title=self.title)

    @property
    def typ(self) -> datatypes.AdmonitionTypeStr:
        return self.attributes["type"]

    @typ.setter
    def typ(self, value: datatypes.AdmonitionTypeStr):
        self.attributes["type"] = value

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += "MkAdmonitionBlock is an admonition based on new pymdownx block syntax."
        url = "https://facelessuser.github.io/pymdown-extensions/extensions/blocks/api/"
        page += mk.MkLink(url, "More info", as_button=True)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in get_args(datatypes.AdmonitionTypeStr):
            page += mk.MkHeader(f"Type '{typ}'", level=3)
            title = f"Block admonition with type {typ!r}"
            content = f"This is type **{typ}**"
            node = mk.MkAdmonitionBlock(typ=typ, content=content, title=title)
            page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    tab = MkAdmonitionBlock(content="test", title="test")
    print(tab)

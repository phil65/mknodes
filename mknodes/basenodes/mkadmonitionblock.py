from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mkblock, mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

AdmonitionTypeStr = Literal[
    "node",
    "abstract",
    "info",
    "tip",
    "success",
    "question",
    "warning",
    "failure",
    "danger",
    "bug",
    "example",
    "quote",
]


class MkAdmonitionBlock(mkblock.MkBlock):
    """Pymdownx-based Admonition Block."""

    ICON = "octicons/info-16"
    REQUIRED_EXTENSIONS = ["pymdownx.blocks.admonition"]

    def __init__(
        self,
        content: str | list | mknode.MkNode,
        *,
        typ: AdmonitionTypeStr = "info",
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
        from mknodes.basenodes import mktext

        if len(self.items) == 1 and isinstance(self.items[0], mktext.MkText):
            content = str(self.items[0])
        elif len(self.items) == 1:
            content = self.items[0]
        else:
            content = [str(i) if isinstance(i, mktext.MkText) else i for i in self.items]
        return helpers.get_repr(self, content=content, typ=self.typ, title=self.title)

    @property
    def typ(self) -> AdmonitionTypeStr:
        return self.attributes["type"]

    @typ.setter
    def typ(self, value: AdmonitionTypeStr):
        self.attributes["type"] = value

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu

        page += "MkAdmonitionBlock is an admonition based on new pymdownx block syntax."
        url = "https://facelessuser.github.io/pymdown-extensions/extensions/blocks/api/"
        page += mknodes.MkLink(url, "More info", as_button=True)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in AdmonitionTypeStr.__args__:
            page += mknodes.MkHeader(f"Type '{typ}'", level=3)
            title = f"Block admonition with type {typ!r}"
            content = f"This is type **{typ}**"
            node = mknodes.MkAdmonitionBlock(typ=typ, content=content, title=title)
            page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    tab = MkAdmonitionBlock(content="test", title="test")
    print(tab)

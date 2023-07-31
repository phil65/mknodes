from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes import mkblock, mknode


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
    """Admonition info box."""

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

    @property
    def typ(self) -> AdmonitionTypeStr:
        return self.attributes["type"]

    @typ.setter
    def typ(self, value: AdmonitionTypeStr):
        self.attributes["type"] = value

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.metadata["status"] = "new"

        page += "MkAdmonitionBlock is an admonition based on new pymdownx block syntax."
        url = "https://facelessuser.github.io/pymdown-extensions/extensions/blocks/api/"
        page += mknodes.MkLink(url, "More info", as_button=True)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in AdmonitionTypeStr.__args__:
            node = mknodes.MkAdmonitionBlock(
                typ=typ,
                content=f"This is type **{typ}**",
                title=f"Block admonition with type {typ!r}",
                header=f"Type '{typ}'",
            )
            page += node
            page += mknodes.MkCode(str(node), language="markdown")


if __name__ == "__main__":
    tab = MkAdmonitionBlock(content="test", title="test")
    print(tab)

from __future__ import annotations

import logging
import textwrap

from typing import Literal

from mknodes import mkcontainer, mknode
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


class MkAdmonition(mkcontainer.MkContainer):
    """Admonition info box."""

    def __init__(
        self,
        content: str | list | mknode.MkNode,
        *,
        typ: AdmonitionTypeStr = "info",
        title: str | None = None,
        collapsible: bool = False,
        expanded: bool = False,
        **kwargs,
    ):
        super().__init__(content=content, **kwargs)
        self.typ = typ
        self.title = title
        self.collapsible = collapsible
        self.expanded = expanded

    def __repr__(self):
        return helpers.get_repr(self, content=self.items, typ=self.typ, title=self.title)

    def _to_markdown(self) -> str:
        if not self.items and not self.title:
            return ""
        block_start = "???" if self.collapsible else "!!!"
        if self.collapsible and self.expanded:
            block_start += "+"
        title = f' "{self.title}"' if self.title else ""
        text = textwrap.indent("\n".join(str(i) for i in self.items), "    ")
        return f"{block_start} {self.typ}{title}\n{text}\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = mknodes.MkAdmonition("The MkAdmonition node is used to show Admonitions.")
        page += node
        page += "This is the resulting code:"
        page += mknodes.MkCode(str(node))
        for typ in [
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
        ]:
            page += mknodes.MkAdmonition(
                typ=typ,
                content=f"This is type {typ}",
                title=typ,
            )
        page += mknodes.MkAdmonition(
            content="Admonitions can also be collapsible",
            collapsible=True,
            title="Expand me!",
        )
        page += mknodes.MkAdmonition(
            content="The initial state can also changed for collapsible admonitions.",
            collapsible=True,
            expanded=True,
            title="Collapse me!",
        )


if __name__ == "__main__":
    admonition = MkAdmonition("")
    print(admonition)

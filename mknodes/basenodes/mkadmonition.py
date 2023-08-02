from __future__ import annotations

import logging
import textwrap

from typing import Any, Literal

from mknodes.basenodes import mkcontainer, mknode
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

    ICON = "octicons/info-16"
    REQUIRED_EXTENSIONS = ["admonition", "pymdownx.details", "pymdownx.superfences"]

    def __init__(
        self,
        content: str | list | mknode.MkNode,
        *,
        typ: AdmonitionTypeStr = "info",
        title: str | None = None,
        collapsible: bool = False,
        expanded: bool = False,
        inline: Literal["left", "right"] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Admonition content
            typ: Admonition type
            title: Optional Admonition title
            collapsible: Whether Admontion can get collapsed by user
            expanded: Initial state if collapsible is set
            inline: Whether admonition should rendered as inline block
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.typ = typ
        self.title = title
        self.collapsible = collapsible
        self.inline = inline
        self.expanded = expanded

    def __repr__(self):
        from mknodes.basenodes import mktext

        if len(self.items) == 1 and isinstance(self.items[0], mktext.MkText):
            content = str(self.items[0])
        elif len(self.items) == 1:
            content = self.items[0]
        else:
            content = [str(i) if isinstance(i, mktext.MkText) else i for i in self.items]
        return helpers.get_repr(self, content=content, typ=self.typ, title=self.title)

    def _to_markdown(self) -> str:
        if not self.items and not self.title:
            return ""
        block_start = "???" if self.collapsible else "!!!"
        if self.collapsible and self.expanded:
            block_start += "+"
        if self.inline:
            inline_label = " inline" if self.inline == "left" else " inline end"
        else:
            inline_label = ""
        title = f' "{self.title}"' if self.title else ""
        text = textwrap.indent("\n".join(str(i) for i in self.items), "    ")
        return f"{block_start} {self.typ}{inline_label}{title}\n{text}\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = mknodes.MkAdmonition("The MkAdmonition node is used to show Admonitions.")
        page += mknodes.MkNodeExample(node)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in AdmonitionTypeStr.__args__:
            node = mknodes.MkAdmonition(
                typ=typ,
                content=f"This is type {typ}",
                title=typ,
                header=f"Type '{typ}'",
            )
            page += mknodes.MkNodeExample(node)
        node = mknodes.MkAdmonition(
            content="Admonitions can also be collapsible.",
            collapsible=True,
            title="Expand me!",
            expanded=True,  # this changes the initial state to expanded
            header="Collapsible and expandable",
        )
        page += mknodes.MkNodeExample(node)
        node = mknodes.MkAdmonition(
            content="Inlined.",
            inline="left",
            title="Inlined.",
            header="Inlined",
        )
        page += mknodes.MkNodeExample(node)


if __name__ == "__main__":
    admonition = MkAdmonition("")
    print(admonition)

from __future__ import annotations

import textwrap

from typing import Any, Literal, get_args

from mknodes.basenodes import mkcontainer, mknode
from mknodes.data import datatypes
from mknodes.utils import helpers, log, reprhelpers


logger = log.get_logger(__name__)


class MkAdmonition(mkcontainer.MkContainer):
    """Admonition info box."""

    ICON = "octicons/info-16"
    REQUIRED_EXTENSIONS = ["admonition", "pymdownx.details", "pymdownx.superfences"]

    def __init__(
        self,
        content: str | list | mknode.MkNode,
        *,
        typ: datatypes.AdmonitionTypeStr = "info",
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
        self.typ = typ
        self.title = title
        self.collapsible = collapsible
        self.inline = inline
        self.expanded = expanded
        super().__init__(content=content, **kwargs)

    def __repr__(self):
        if len(self.items) == 1:
            content = helpers.to_str_if_textnode(self.items[0])
        else:
            content = [helpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(self, content=content, typ=self.typ, title=self.title)

    def attach_annotations(self, text: str) -> str:
        # we deal with attaching annotations ourselves.
        return text

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
        if self.annotations:
            ann_marker = " annotate"
            annotations = f"\n{self.annotations}\n"
        else:
            ann_marker = ""
            annotations = ""
        title = f' "{self.title}"' if self.title is not None else ""
        text = "\n".join(i.to_markdown() for i in self.items)
        indented = textwrap.indent(text, "    ")
        optional = ann_marker + inline_label
        return f"{block_start} {self.typ}{optional}{title}\n{indented}\n{annotations}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = mknodes.MkAdmonition("MkAdmonitions can carry annotations(1).")
        node.annotations[1] = "Super handy!"
        page += mknodes.MkReprRawRendered(node)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in get_args(datatypes.AdmonitionTypeStr):
            page += mknodes.MkHeader(f"Type '{typ}'", level=3)
            content = f"This is type **{typ}**"
            node = mknodes.MkAdmonition(typ=typ, content=content)
            page += mknodes.MkReprRawRendered(node)
        page += mknodes.MkHeader("Collapsible and expandable", level=3)
        node = mknodes.MkAdmonition(
            content="Admonitions can also be collapsible.",
            collapsible=True,
            title="Expand me!",
            expanded=True,  # this changes the initial state to expanded
        )
        page += mknodes.MkReprRawRendered(node)
        page += mknodes.MkHeader("Inlined", level=3)
        node = mknodes.MkAdmonition(content="Inlined.", inline="left", title="Inlined.")
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    admonition = MkAdmonition("")
    print(admonition)

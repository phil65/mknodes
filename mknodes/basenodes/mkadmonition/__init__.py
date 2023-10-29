from __future__ import annotations

import textwrap

from typing import Any, Literal, get_args

from mknodes.basenodes import mkcontainer, mknode
from mknodes.data import datatypes
from mknodes.utils import log, reprhelpers, resources


logger = log.get_logger(__name__)


class MkAdmonition(mkcontainer.MkContainer):
    """Admonition info box."""

    ICON = "octicons/info-16"
    ATTR_LIST_SEPARATOR = "    "
    REQUIRED_EXTENSIONS = [
        resources.Extension("admonition"),
        resources.Extension("pymdownx.details"),
        resources.Extension("pymdownx.superfences"),
    ]

    def __init__(
        self,
        content: str | list | mknode.MkNode,
        *,
        typ: datatypes.AdmonitionTypeStr | str = "info",
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
            content = reprhelpers.to_str_if_textnode(self.items[0])
        else:
            content = [reprhelpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(
            self,
            content=content,
            typ=self.typ if self.typ != "info" else None,
            title=self.title,
            collapsible=self.collapsible,
            expanded=self.expanded,
            _filter_empty=True,
            _filter_false=True,
        )

    def attach_annotations(self, text: str) -> str:
        # we deal with attaching annotations ourselves.
        return text

    @property
    def title_line(self):
        block_start = "???" if self.collapsible else "!!!"
        if self.collapsible and self.expanded:
            block_start += "+"
        if self.inline:
            inline_label = " inline" if self.inline == "left" else " inline end"
        else:
            inline_label = ""
        ann_marker = " annotate" if self.annotations else ""
        title = f' "{self.title}"' if self.title is not None else ""
        optional = ann_marker + inline_label
        return f"{block_start} {self.typ}{optional}{title}"

    def _to_markdown(self) -> str:
        if not self.items and not self.title:
            return ""
        annotations = f"\n{self.annotations}\n" if self.annotations else ""
        text = "\n".join(i.to_markdown() for i in self.items)
        indented = textwrap.indent(text, "    ")
        return f"{self.title_line}\n{indented}\n{annotations}"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = mk.MkAdmonition("MkAdmonitions can carry annotations(1).")
        node.annotations[1] = "Super handy!"
        page += mk.MkReprRawRendered(node)
        # AdmonitionTypeStr is a Literal containing all Admonition types
        for typ in get_args(datatypes.AdmonitionTypeStr):
            page += mk.MkHeader(f"Type '{typ}'", level=3)
            content = f"This is type **{typ}**"
            node = mk.MkAdmonition(typ=typ, content=content)
            page += mk.MkReprRawRendered(node)
        page += mk.MkHeader("Collapsible and expandable", level=3)
        node = mk.MkAdmonition(
            content="Admonitions can also be collapsible.",
            collapsible=True,
            title="Expand me!",
            expanded=True,  # this changes the initial state to expanded
        )
        page += mk.MkReprRawRendered(node)
        page += mk.MkHeader("Inlined", level=3)
        node = mk.MkAdmonition(content="Inlined.", inline="left", title="Inlined.")
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    admonition = MkAdmonition("")
    print(admonition)

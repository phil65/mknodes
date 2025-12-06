from __future__ import annotations

import textwrap

from typing import Any, Literal, TYPE_CHECKING

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, resources

if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    from mknodes.data import datatypes


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
        content: str | list[mknode.MkNode] | mknode.MkNode,
        *,
        typ: datatypes.AdmonitionTypeStr | str = "info",
        title: str | None = None,
        collapsible: bool = False,
        expanded: bool = False,
        inline: Literal["left", "right"] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
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

    def attach_annotations(self, text: str) -> str:
        # we deal with attaching annotations ourselves.
        return text

    @property
    def title_line(self) -> str:
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

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get markdown with custom admonition formatting and resources."""
        items = self.get_items()
        if not items and not self.title:
            return resources.NodeContent(
                markdown="",
                resources=await self._build_node_resources(),
            )

        # Collect content from children
        child_contents = [await item.get_content() for item in items]

        # Build markdown with admonition formatting
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        text = "\n".join(child_markdowns)
        indented = textwrap.indent(text, "    ")
        annotations = f"\n{self.annotations}\n" if self.annotations else ""
        md = f"{self.title_line}\n{indented}\n{annotations}"

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":
    admonition = MkAdmonition("fdsf", collapsible=True)
    print(repr(admonition))

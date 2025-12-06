from __future__ import annotations

import textwrap

from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mkblock, mkcontainer
from mknodes.utils import log, reprhelpers, resources


if TYPE_CHECKING:
    from mknodes.basenodes import mknode


logger = log.get_logger(__name__)


class MkTabBlock(mkblock.MkBlock):
    """Node representing a single tab (new block style)."""

    ICON = "material/tab"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.blocks.tab")]

    def __init__(
        self,
        content: str | mknode.MkNode | list[Any] | None = None,
        title: str = "",
        *,
        new: bool | None = None,
        select: bool | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            title: Tab title
            content: Tab content
            new: Whether tab should start a new tab bloock
            select: Whether tab should be initially selected
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("tab", content=content or [], argument=title, **kwargs)
        if new is not None:
            self.new = new
        if select is not None:
            self.select = select

    @property
    def title(self) -> str:
        return self.argument

    @title.setter
    def title(self, value: str) -> None:
        self.argument = value

    @property
    def new(self) -> bool:
        return self.attributes.get("new", False)

    @new.setter
    def new(self, value: bool) -> None:
        self.attributes["new"] = value

    @property
    def select(self) -> bool:
        return self.attributes.get("select", False)

    @select.setter
    def select(self, value: bool) -> None:
        self.attributes["select"] = value


class MkTab(mkcontainer.MkContainer):
    """Node representing a single tab."""

    ICON = "material/tab"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.tabbed")]
    ATTR_LIST_SEPARATOR = "    "

    def __init__(
        self,
        content: list[Any] | str | mknode.MkNode | None = None,
        title: str = "",
        *,
        new: bool = False,
        select: bool = False,
        attrs: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            title: Tab title
            content: Tab content
            new: Whether tab should start a new tab bloock
            select: Whether tab should be initially selected
            attrs: Additional attributes for the tab
            kwargs: Keyword arguments passed to parent
        """
        self.title = title
        self.select = select
        self.new = new
        self.attrs = attrs
        super().__init__(content=content, **kwargs)

    def __repr__(self) -> str:
        content: str | list[str]
        items = self.get_items()
        if len(items) == 1:
            content = reprhelpers.to_str_if_textnode(items[0])
        else:
            content = [reprhelpers.to_str_if_textnode(i) for i in items]
        return reprhelpers.get_repr(
            self,
            title=self.title,
            content=content,
            select=self.select,
            new=self.new,
            attrs=self.attrs,
            _filter_empty=True,
            _filter_false=True,
        )

    def attach_annotations(self, text: str) -> str:
        # we deal with attaching annotations ourselves.
        return text

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with tab formatting and resources."""
        items = self.get_items()

        # Collect content from children
        child_contents = [await item.get_content() for item in items]

        # Build markdown with tab formatting
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        text = "\n\n".join(child_markdowns)
        text = text.rstrip("\n")
        if self.annotations:
            annotates = str(self.annotations)
            text = f"{text}\n{{ .annotate }}\n\n{annotates}"
        text = textwrap.indent(text, prefix="    ")
        if self.new:
            mark = "!"
        elif self.select:
            mark = "+"
        else:
            mark = ""
        lines = [f'==={mark} "{self.title}"', text]
        md = "\n".join(lines) + "\n"

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":
    tab = MkTabBlock(content="test", title="test", new=True)
    print(tab)

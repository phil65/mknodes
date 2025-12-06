from __future__ import annotations

from collections.abc import Mapping
import textwrap

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mkcontainer, mktext
from mknodes.utils import log, reprhelpers, resources


if TYPE_CHECKING:
    import mknodes as mk

logger = log.get_logger(__name__)


class MkFootNote(mkcontainer.MkContainer):
    """Represents a single footnote. It gets managed by an MkFootNotes node."""

    REQUIRED_EXTENSIONS = [resources.Extension("footnotes")]

    def __init__(
        self,
        num: int,
        content: str | mk.MkNode,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            num: Footnote index number
            content: Footnote content
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.num = num

    def __repr__(self) -> str:
        return reprhelpers.get_repr(self, num=self.num, content=self.get_items())

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with footnote formatting and resources."""
        items = self.get_items()

        # Collect content from children
        child_contents = [await item.get_content() for item in items]

        # Build markdown with footnote formatting
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        item_str = "\n".join(child_markdowns)
        indented = textwrap.indent(item_str, "    ")
        md = f"[^{self.num}]:\n{indented}\n"

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


class MkFootNotes(mkcontainer.MkContainer):
    """Node containing a list of MkFootNotes."""

    ICON = "octicons/list-ordered-16"
    REQUIRED_EXTENSIONS = [resources.Extension("footnotes")]

    def __init__(
        self,
        footnotes: (Mapping[int, str | mk.MkNode] | list[MkFootNote] | list[str] | None) = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            footnotes: Footnotes data (Can be given in different shapes)
            kwargs: Keyword arguments passed to parent
        """
        match footnotes:
            case None:
                items = []
            case list():
                items = [
                    (
                        ann if isinstance(ann, MkFootNote) else MkFootNote(i, ann)  # type: ignore
                    )
                    for i, ann in enumerate(footnotes, start=1)
                ]
            case Mapping():
                items = [MkFootNote(k, content=v) for k, v in footnotes.items()]
            case _:
                raise TypeError(footnotes)
        super().__init__(content=items, **kwargs)

    def get_items(self) -> list[MkFootNote]:  # type: ignore[override]
        """Return the list of footnotes."""
        return self._items  # type: ignore[return-value]

    def __repr__(self) -> str:
        notes: list[mk.MkNode | str] = []
        for item in self.get_items():
            item_children = item.get_items()
            if len(item_children) == 1 and isinstance(item_children[0], mktext.MkText):
                notes.append(str(item_children[0]))
            elif len(item_children) == 1:
                notes.append(item_children[0])
            else:
                notes.append(item)
        return reprhelpers.get_repr(self, footnotes=notes)

    def __getitem__(self, index: int) -> MkFootNote:
        for node in self.get_items():
            if node.num == index:
                return node
        raise IndexError(index)

    def __contains__(self, item: int | MkFootNote) -> bool:
        match item:
            case MkFootNote():
                return item in self.get_items()
            case int():
                return any(i.num == item for i in self.get_items())
            case _:
                raise TypeError(item)

    def _get_item_pos(self, num: int) -> int:
        items = self.get_items()
        item = next(i for i in items if i.num == num)
        return items.index(item)

    def __setitem__(self, index: int, value: mk.MkNode | str) -> None:
        match value:
            case MkFootNote():
                node = value
            case _:
                node = MkFootNote(index, content=value, parent=self)
        items = self.get_items()
        if index in self:
            pos = self._get_item_pos(index)
            items[pos] = node
        else:
            items.append(node)

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content from sorted footnotes and resources."""
        items = self.get_items()
        if not items:
            return resources.NodeContent(
                markdown="",
                resources=await self._build_node_resources(),
            )

        items = sorted(items, key=lambda x: x.num)

        # Collect content from children
        child_contents = [await item.get_content() for item in items]

        # Build markdown - children already formatted
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        md = "".join(child_markdowns)

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":
    import mknodes as mk

    # ann = MkFootNote(1, "test")
    # print(ann)
    page = mk.MkPage()
    print(page)

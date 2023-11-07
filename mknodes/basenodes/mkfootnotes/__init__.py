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
    ):
        """Constructor.

        Arguments:
            num: Footnote index number
            content: Footnote content
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.num = num

    def __repr__(self):
        return reprhelpers.get_repr(self, num=self.num, content=self.items)

    def _to_markdown(self) -> str:
        item_str = "\n".join(i.to_markdown() for i in self.items)
        indented = textwrap.indent(item_str, "    ")
        return f"[^{self.num}]:\n{indented}\n"


class MkFootNotes(mkcontainer.MkContainer):
    """Node containing a list of MkFootNotes."""

    items: list[MkFootNote]
    ICON = "octicons/list-ordered-16"
    REQUIRED_EXTENSIONS = [resources.Extension("footnotes")]

    def __init__(
        self,
        footnotes: (
            Mapping[int, str | mk.MkNode] | list[MkFootNote] | list[str] | None
        ) = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
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

    def __repr__(self):
        notes: list[mk.MkNode | str] = []
        for item in self.items:
            if len(item.items) == 1 and isinstance(item.items[0], mktext.MkText):
                notes.append(str(item.items[0]))
            elif len(item.items) == 1:
                notes.append(item.items[0])
            else:
                notes.append(item)
        return reprhelpers.get_repr(self, footnotes=notes)

    def __getitem__(self, index: int):
        for node in self.items:
            if node.num == index:
                return node
        raise IndexError(index)

    def __contains__(self, item: int | MkFootNote) -> bool:
        match item:
            case MkFootNote():
                return item in self.items
            case int():
                return any(i.num == item for i in self.items)
            case _:
                raise TypeError(item)

    def _get_item_pos(self, num: int) -> int:
        item = next(i for i in self.items if i.num == num)
        return self.items.index(item)

    def __setitem__(self, index: int, value: mk.MkNode | str):
        match value:
            case MkFootNote():
                node = value
            case _:
                node = MkFootNote(index, content=value, parent=self)
        if index in self:
            pos = self._get_item_pos(index)
            self.items[pos] = node
        else:
            self.items.append(node)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkFootNotes()
        page += "The MkFootNotes node aggregates footnotes[^1]."
        node[1] = r"Footnotes are numbered, can be set via \__setitem__."
        node[2] = r"They can also get nested[^3]."
        node[3] = mk.MkAdmonition("And they can also contain other Markdown.")
        page += node
        page += mk.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        if not self.items:
            return ""
        items = sorted(self.items, key=lambda x: x.num)
        return "".join(i.to_markdown() for i in items)


if __name__ == "__main__":
    import mknodes as mk

    # ann = MkFootNote(1, "test")
    # print(ann)
    page = mk.MkPage()
    MkFootNotes.create_example_page(page)
    print(page)

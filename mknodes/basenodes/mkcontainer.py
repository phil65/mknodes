from __future__ import annotations

from collections.abc import Iterator
import re

from typing import Any

from mknodes.basenodes import mkheader, mknode, mktext
from mknodes.utils import helpers, log, reprhelpers


HEADER_REGEX = re.compile(r"^(#{1,6}) (.*)")

logger = log.get_logger(__name__)


class MkContainer(mknode.MkNode):
    """A base class for Nodes containing other MkNodes."""

    ICON = "material/database"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        block_separator: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Child Nodes of this container
            block_separator: Separator to put between blocks. Defaults to 2 linebreaks
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.items: list[mknode.MkNode] = []
        self.block_separator = "\n\n" if block_separator is None else block_separator
        match content:
            case None:
                items: list[mknode.MkNode] = []
            case str():
                items = [self.to_child_node(content)] if content else []
            case mknode.MkNode():
                items = [self.to_child_node(content)]
            case list():
                items = [self.to_child_node(i) for i in content]
            case _:
                raise TypeError(content)
        for item in items:
            self.append(item)

    def __bool__(self):
        return bool(self.items)

    def __add__(self, other: str | mknode.MkNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[mknode.MkNode]:  # type: ignore
        return iter(self.items)

    def __repr__(self):
        content = [helpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(self, content=content)

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "MkContainers are usually only used as a base class"
        page += "It basically only carries other nodes and stringifies them sequentially."
        item_1 = mknodes.MkCode(code="a = 1 + 2")
        item_2 = mktext.MkText("abc")
        node = MkContainer(content=[item_1, item_2])
        page += mknodes.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        return self.block_separator.join(i.to_markdown() for i in self.items)

    def append(self, other: str | mknode.MkNode):
        node = self.to_child_node(other)
        self.items.append(node)  # type: ignore[arg-type]

    def insert(self, index: int, other: str | mknode.MkNode):
        node = self.to_child_node(other)
        self.items.insert(index, node)

    def to_child_node(self, other) -> mknode.MkNode:  # type: ignore[return]
        match other:
            case str() if (match := HEADER_REGEX.match(other)) and "\n" not in other:
                return mkheader.MkHeader(match[2], level=len(match[1]), parent=self)
            case str():
                return mktext.MkText(other, parent=self)
            case mknode.MkNode():
                other.parent = self
                return other
            case _:
                raise TypeError(other)

    @property  # type: ignore
    def children(self) -> list[mknode.MkNode]:
        return self.items

    @children.setter
    def children(self, children: list[mknode.MkNode]):
        self.items = children


if __name__ == "__main__":
    section = MkContainer(header="fff")
    print(section)

from __future__ import annotations

from collections.abc import Iterator

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkContainer(mknode.MkNode):
    """A node containing other MkNodes.

    This node class is often used as a base class, and can be treated like a list.
    Nodes added to a container are automatically re-parented.
    """

    ICON = "material/database"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        *,
        block_separator: str = "\n\n",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Child Nodes of this container
            block_separator: Separator to put between blocks. Defaults to 2 linebreaks
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.block_separator = block_separator
        match content:
            case None:
                self.items: list[mknode.MkNode] = []
            case str():
                self.items = [self.to_child_node(content)] if content else []
            case mknode.MkNode():
                self.items = [self.to_child_node(content)]
            case list():
                self.items = [self.to_child_node(i) for i in content]
            case _:
                raise TypeError(content)

    def __bool__(self):
        return bool(self.items)

    def __add__(self, other: str | mknode.MkNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[mknode.MkNode]:  # type: ignore
        return iter(self.items)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        item_1 = mk.MkCode("a = 1 + 2")
        item_2 = mk.MkText("abc")
        node = MkContainer(content=[item_1, item_2])
        page += mk.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        return self.block_separator.join(i.to_markdown() for i in self.items)

    def append(self, other: str | mknode.MkNode):
        """Append a MkNode to the end of given MkPage.

        Arguments:
            other: The node / text to append
        """
        node = self.to_child_node(other)
        self.items.append(node)  # type: ignore[arg-type]

    def insert(self, index: int, other: str | mknode.MkNode):
        """Insert a MkNode into desired position of given MkPage.

        Arguments:
            index: Position where node should get inserted
            other: The node / text to insert
        """
        node = self.to_child_node(other)
        self.items.insert(index, node)

    @property  # type: ignore
    def children(self) -> list[mknode.MkNode]:
        return self.items

    @children.setter
    def children(self, children: list[mknode.MkNode]):
        self.items = children


if __name__ == "__main__":
    section = MkContainer(header="fff")
    print(section)

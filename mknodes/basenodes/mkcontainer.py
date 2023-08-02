from __future__ import annotations

from collections.abc import Iterator
import logging

from typing import Any

from mknodes.basenodes import mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkContainer(mknode.MkNode):
    """A base class for Nodes containing other MkNodes."""

    ICON = "material/database"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Child Nodes of this container
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.items: list[mknode.MkNode] = []
        match content:
            case None:
                items: list[mknode.MkNode] = []
            case str():
                items = [mktext.MkText(content)] if content else []
            case mknode.MkNode():
                items = [content]
            case list():
                items = [mktext.MkText(i) if isinstance(i, str) else i for i in content]
            case _:
                raise TypeError(content)
        for item in items or []:
            self.append(item)  # noqa: PERF402

    def __add__(self, other: str | mknode.MkNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[mknode.MkNode]:  # type: ignore
        return iter(self.items)

    def __repr__(self):
        content = [str(i) if isinstance(i, mktext.MkText) else i for i in self.items]
        return helpers.get_repr(self, content=content)

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "MkContainers are usually only used as a base class"
        page += "It basically only carries other nodes and stringifies them sequentially."
        item_1 = mknodes.MkCode(code="a = 1 + 2")
        item_2 = mktext.MkText("abc")
        node = MkContainer(content=[item_1, item_2])
        page += mknodes.MkNodeExample(node, indent=True)

    def _to_markdown(self) -> str:
        return "\n\n".join(i.to_markdown() for i in self.items)

    def append(self, other: str | mknode.MkNode):
        match other:
            case str():
                other = mktext.MkText(other, parent=self)
            case mknode.MkNode():
                other.parent_item = self
            case _:
                raise TypeError(other)
        self.items.append(other)

    @property  # type: ignore
    def children(self) -> list[mknode.MkNode]:
        return self.items

    @children.setter
    def children(self, children: list[mknode.MkNode]):
        self.items = children


if __name__ == "__main__":
    section = MkContainer(header="fff")
    for example in MkContainer.examples():
        container = MkContainer(**example)
        print(container)

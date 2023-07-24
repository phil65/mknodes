from __future__ import annotations

from collections.abc import Iterator
import logging

from mknodes import mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkContainer(mknode.MkNode):
    """A base class for Nodes containing other MkNodes."""

    def __init__(self, items: list | None = None, **kwargs):
        super().__init__(**kwargs)
        self.items: list[mknode.MkNode] = []
        for item in items or []:
            self.append(item)  # noqa: PERF402

    def __add__(self, other: str | mknode.MkNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[mknode.MkNode]:  # type: ignore
        return iter(self.items)

    def __repr__(self):
        return helpers.get_repr(self, items=self.items)

    @staticmethod
    def examples():
        from mknodes import mkcode

        yield dict(items=[mkcode.MkCode(code="a = 1 + 2"), mktext.MkText("abc")])

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

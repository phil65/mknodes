from __future__ import annotations

import textwrap
from typing import TYPE_CHECKING

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Hashable, Sequence


logger = log.get_logger(__name__)


class Connector[T]:
    def __init__(self, objects: T | list[T] | tuple[T, ...], max_depth: int | None = None) -> None:
        objs = objects if isinstance(objects, list | tuple) else [objects]
        self.item_dict: dict[Hashable, str] = {}
        self.connections: list[tuple[Hashable, Hashable]] = []
        self.max_depth = max_depth
        self._connect(objs)  # pyright: ignore[reportUnknownArgumentType]

    def _connect(self, objects: Sequence[T]) -> None:
        def add_connections(item: T, depth: int = 0) -> None:
            identifier = self.get_id(item)
            if identifier not in self.item_dict:
                # if item.__module__.startswith(base_module):
                self.item_dict[identifier] = self.get_title(item)
                if self.max_depth and self.max_depth <= depth:
                    return
                for base in self.get_children(item):
                    self.connections.append((self.get_id(base), identifier))
                    add_connections(base, depth + 1)

        for obj in objects:
            add_connections(obj)

    @property
    def items(self) -> list[Hashable]:
        return list(self.item_dict.keys())

    @property
    def titles(self) -> list[str]:
        return list(self.item_dict.values())

    def get_children(self, item: T) -> list[T] | tuple[T, ...]:  # pyright: ignore[reportUnusedParameter]
        """This should return a list of children for the tree node."""
        return NotImplemented

    def get_id(self, item: T):
        """This needs to return a unique identifier for an item."""
        return item

    def get_attributes(self, item: T) -> list[str] | None:  # pyright: ignore[reportUnusedParameter]
        return None

    def get_title(self, item: T) -> str:
        """This can be overridden for a nicer label."""
        return str(self.get_id(item))

    def get_graph_connection_text(self) -> str:
        lines = [f'{identifier}["{title}"]' for identifier, title in zip(self.items, self.titles)]
        lines += [f"{a} --> {b}" for a, b in self.connections]
        return textwrap.indent("\n".join(lines), "  ")


if __name__ == "__main__":

    class Test(Connector[type]):
        def get_children(self, item: type):
            return item.__bases__

    test = Test(Connector).get_graph_connection_text()
    print(test)

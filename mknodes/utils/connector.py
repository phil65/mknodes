from __future__ import annotations

from collections.abc import Hashable
import logging
import textwrap


logger = logging.getLogger(__name__)


class Connector:
    def __init__(self, objects, max_depth: int | None = None):
        if not isinstance(objects, list | tuple):
            objects = [objects]
        self.item_dict: dict[Hashable, str] = {}
        self.connections: list[tuple[Hashable, Hashable]] = []
        self.max_depth = max_depth
        self._connect(objects)

    def _connect(self, objects):
        def add_connections(item, depth: int = 0):
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
    def items(self):
        return list(self.item_dict.keys())

    @property
    def titles(self):
        return list(self.item_dict.values())

    def get_children(self, item) -> list | tuple:
        """This should return a list of children for the tree node."""
        return NotImplemented

    def get_id(self, item):
        """This needs to return a unique identifier for an item."""
        return item

    def get_attributes(self, item):
        return None

    def get_title(self, item) -> str:
        """This can be overridden for a nicer label."""
        return str(self.get_id(item))

    def get_graph_connection_text(self):
        lines = [
            f'{identifier}["{title}"]'
            for identifier, title in zip(self.items, self.titles)
        ]
        lines += [f"{a} --> {b}" for a, b in self.connections]
        return textwrap.indent("\n".join(lines), "  ")


if __name__ == "__main__":

    class Test(Connector):
        def get_children(self, item):
            return item.__bases__

    test = Test(Connector).get_graph_connection_text()
    print(test)

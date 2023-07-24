from __future__ import annotations

import logging
import os
import pathlib
import types

from mkdocstrings import inventory


logger = logging.getLogger(__name__)


class InventoryManager:
    def __init__(self):
        self.inv_files: set[inventory.Inventory] = set()

    def add_inv_file(self, path: str | os.PathLike):
        with pathlib.Path(path).open("rb") as file:
            inv = inventory.Inventory.parse_sphinx(file)
        self.inv_files.add(inv)

    def __getitem__(self, name: str | type | types.FunctionType | types.MethodType):
        match name:
            case type():
                path = f"{name.__module__}.{name.__qualname__}"
            case str():
                path = name
            case _:
                raise TypeError(name)
        for inv_file in self.inv_files:
            if path in inv_file:
                return inv_file[path]
        return None


if __name__ == "__main__":
    inv_manager = InventoryManager()

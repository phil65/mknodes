from __future__ import annotations

import abc

from collections.abc import Mapping
import itertools
import logging
import os
import pathlib
import types

from mkdocstrings import inventory


logger = logging.getLogger(__name__)


class InventoryManager(Mapping, metaclass=abc.ABCMeta):
    def __init__(self):
        self.inv_files: list[inventory.Inventory] = []

    def add_inv_file(self, path: str | os.PathLike):
        with pathlib.Path(path).open("rb") as file:
            inv = inventory.Inventory.parse_sphinx(file)
        self.inv_files.append(inv)

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
        raise KeyError(name)

    def __iter__(self):
        return itertools.chain(*[inv_file.keys() for inv_file in self.inv_files])

    def __len__(self):
        return sum(len(i) for i in self.inv_files)


if __name__ == "__main__":
    inv_manager = InventoryManager()
    inv_manager.add_inv_file("mknodes/utils/objects.inv")
    file = inv_manager.inv_files[0]
    print(len(inv_manager))

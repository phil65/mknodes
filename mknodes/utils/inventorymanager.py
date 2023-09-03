from __future__ import annotations

import abc

from collections.abc import Mapping
import io
import itertools
import logging
import os
import pathlib
import posixpath
import types

from mkdocstrings import inventory

from mknodes.utils import cache, helpers


logger = logging.getLogger(__name__)


class Inventory(inventory.Inventory):
    def __init__(self, base_url: str):
        self.base_url = base_url

    @classmethod
    def from_file(
        cls,
        path: str | os.PathLike | io.BytesIO,
        base_url: str,
        *,
        domains: list[str] | None = None,
    ):  # sourcery skip: assign-if-exp
        inv = cls(base_url)
        domains = domains or ["py"]
        if isinstance(path, io.BytesIO):  # noqa: SIM108
            file = path
        else:
            file = pathlib.Path(path).open("rb")  # noqa: SIM115
        with file:
            inv_dict = inventory.Inventory.parse_sphinx(file, domain_filter=domains)
        inv.update(inv_dict)
        return inv

    @classmethod
    def from_url(
        cls,
        url: str,
        *,
        base_url: str | None = None,
        domains: list[str] | None = None,
    ):
        data = cache.download_and_cache_url(url, days=1)
        buffer = io.BytesIO(data)
        if base_url is None:
            base_url = os.path.dirname(url)  # noqa: PTH120
        return cls.from_file(buffer, base_url or "", domains=domains)

    def __getitem__(self, value):
        val = super().__getitem__(value)
        return posixpath.join(self.base_url, val.uri)


class InventoryManager(Mapping, metaclass=abc.ABCMeta):
    # TODO: might be worth using collections.ChainMap, or just merging all inv files.

    def __init__(self):
        self.inv_files: list[inventory.Inventory] = []

    def add_inv_file(
        self,
        path: str | os.PathLike,
        base_url: str | None = None,
        domains: list[str] | None = None,
    ):
        path = str(path)
        if helpers.is_url(path):
            inv = Inventory.from_url(path, base_url=base_url, domains=domains)
        elif base_url:
            inv = Inventory.from_file(path, domains=domains, base_url=base_url)
        else:
            msg = "Base URL needed for loading from file."
            raise ValueError(msg)
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
    inv_manager.add_inv_file("tests/data/objects.inv", base_url="http://test.de")
    file = inv_manager.inv_files[0]
    item = inv_manager["prettyqt.widgets.widget.WidgetMixin.set_style"]
    # print(item)
    inv = Inventory.from_url("https://docs.python.org/3/objects.inv")
    print(inv)
    # print(inv_manager["prettyqt.widgets.widget.WidgetMixin.set_style"])
    # print(file)

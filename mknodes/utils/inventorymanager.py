from __future__ import annotations

import abc

from collections.abc import Collection, Mapping
import io
import itertools
import os
import pathlib
import posixpath
import re
import types
from typing import BinaryIO, Self
import zlib

from mknodes.utils import downloadhelpers, helpers, log


logger = log.get_logger(__name__)


INV_HEADER = """\
# Sphinx inventory version 2
# Project: {project}
# Version: {version}
# The remainder of this file is compressed using zlib.
"""


class InventoryItem:
    """Inventory item."""

    def __init__(
        self,
        name: str,
        domain: str,
        role: str,
        uri: str,
        priority: int = 1,
        dispname: str | None = None,
    ):
        """Initialize the object.

        Arguments:
            name: The item name.
            domain: The item domain, like 'python'
            role: The item role, like 'class' or 'method'.
            uri: The item URI.
            priority: The item priority.
            dispname: The item display name.
        """
        self.name: str = name
        self.domain: str = domain
        self.role: str = role
        self.uri: str = uri
        self.priority: int = priority
        self.dispname: str = dispname or name

    def format_sphinx(self) -> str:
        """Format this item as a Sphinx inventory line and return it."""
        dispname = self.dispname
        if dispname == self.name:
            dispname = "-"
        uri = self.uri
        if uri.endswith(self.name):
            uri = uri[: -len(self.name)] + "$"
        return f"{self.name} {self.domain}:{self.role} {self.priority} {uri} {dispname}"

    sphinx_item_regex = re.compile(r"^(.+?)\s+(\S+):(\S+)\s+(-?\d+)\s+(\S+)\s*(.*)$")

    @classmethod
    def parse_sphinx(cls, line: str) -> InventoryItem:
        """Parse a line from a Sphinx v2 inventory file and return an `InventoryItem`.

        Arguments:
            line: The line to parse
        """
        match = cls.sphinx_item_regex.search(line)
        if not match:
            raise ValueError(line)
        name, domain, role, priority, uri, dispname = match.groups()
        if uri.endswith("$"):
            uri = uri[:-1] + name
        if dispname == "-":
            dispname = name
        return cls(name, domain, role, uri, int(priority), dispname)


class BaseInventory(dict):
    """Inventory of collected and rendered objects."""

    def __init__(
        self,
        items: list[InventoryItem] | None = None,
        project: str = "project",
        version: str = "0.0.0",
    ):
        """Initialize the object.

        Arguments:
            items: A list of items.
            project: The project name.
            version: The project version.
        """
        super().__init__()
        items = items or []
        for item in items:
            self[item.name] = item
        self.project = project
        self.version = version

    def register(
        self,
        name: str,
        domain: str,
        role: str,
        uri: str,
        priority: int = 1,
        dispname: str | None = None,
    ) -> None:
        """Create and register an item.

        Arguments:
            name: The item name.
            domain: The item domain, like 'python'
            role: The item role, like 'class' or 'method'.
            uri: The item URI.
            priority: The item priority.
            dispname: The item display name.
        """
        self[name] = InventoryItem(
            name=name,
            domain=domain,
            role=role,
            uri=uri,
            priority=priority,
            dispname=dispname,
        )

    def format_sphinx(self) -> bytes:
        """Format this inventory as a Sphinx `objects.inv` file and return it."""
        header = INV_HEADER.format(project=self.project, version=self.version).encode()
        lines = [
            item.format_sphinx().encode()
            for item in sorted(self.values(), key=lambda item: (item.domain, item.name))
        ]
        return header + zlib.compress(b"\n".join(lines) + b"\n", 9)

    @classmethod
    def parse_sphinx(
        cls,
        in_file: BinaryIO,
        *,
        domain_filter: Collection[str] = (),
    ) -> Self:
        """Parse a Sphinx v2 inventory file and return an `Inventory` from it.

        Arguments:
            in_file: The binary file-like object to read from.
            domain_filter: A collection of domain values to allow.
        """
        for _ in range(4):
            in_file.readline()
        lines = zlib.decompress(in_file.read()).splitlines()
        items = [InventoryItem.parse_sphinx(line.decode()) for line in lines]
        if domain_filter:
            items = [item for item in items if item.domain in domain_filter]
        return cls(items)


class Inventory(BaseInventory):
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
            try:
                inv_dict = BaseInventory.parse_sphinx(file, domain_filter=domains)
            except zlib.error as e:
                logger.warning("Error when parsing Inventory file: %s", e)
                return inv
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
        """Return an Inventory based on an inventory file located at given url.

        Arguments:
            url: Inventory file url
            base_url: The base url for the inventory, if different from download url
            domains: The domains to include
        """
        data = downloadhelpers.download(url)
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
        self.inv_files: list[BaseInventory] = []

    def add_inv_file(
        self,
        path: str | os.PathLike,
        base_url: str | None = None,
        domains: list[str] | None = None,
    ):
        import urllib.error

        path = str(path)
        if helpers.is_url(path):
            logger.debug("Downloading %r...", path)
            try:
                inv = Inventory.from_url(path, base_url=base_url, domains=domains)
                self.inv_files.append(inv)
            except urllib.error.HTTPError:
                logger.debug("No file for %r...", path)
                return
        elif base_url:
            inv = Inventory.from_file(path, domains=domains, base_url=base_url)
            self.inv_files.append(inv)
        else:
            msg = "Base URL needed for loading from file."
            raise ValueError(msg)

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

from __future__ import annotations

from importlib import metadata
import logging
import os
import sys

from mknodes.utils import helpers, inventorymanager


logger = logging.getLogger(__name__)

BUILTIN_URL = "https://docs.python.org/3/library/{mod}.html#{name}"


class LinkProvider:
    def __init__(self):
        self.inv_manager = inventorymanager.InventoryManager()

    def add_inv_file(self, path: str | os.PathLike):
        self.inv_manager.add_inv_file(path)

    def link_for_klass(self, kls: type):
        if kls.__module__ == "builtins":
            url = BUILTIN_URL.format(mod="functions", name=kls.__name__)
            return helpers.linked(url, title=kls.__name__)
        if kls.__module__ in sys.stdlib_module_names:
            mod = kls.__module__
            url = BUILTIN_URL.format(mod=mod, name=f"{mod}.{kls.__name__}")
            return helpers.linked(url, title=kls.__name__)
        try:
            dist = metadata.distribution(kls.__module__.split(".")[0])
        except metadata.PackageNotFoundError:
            return helpers.linked(kls.__qualname__)
        else:
            if url := dist.metadata["Home-Page"]:
                return helpers.linked(url, title=kls.__qualname__)
            return helpers.linked(kls.__qualname__)


if __name__ == "__main__":
    provider = LinkProvider()
    link = provider.link_for_klass(logging.LogRecord)
    print(link)

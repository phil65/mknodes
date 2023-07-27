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
        module = kls.__module__.split(".")[0]
        qual_name = kls.__qualname__.split("[")[0]  # to split off generics part
        if url := self.homepage_for_distro(module):
            return helpers.linked(url, title=qual_name)
        return helpers.linked(qual_name)

    def homepage_for_distro(self, dist_name: str):
        try:
            dist = metadata.distribution(dist_name)
        except metadata.PackageNotFoundError:
            return None
        else:
            return dist.metadata["Home-Page"]


if __name__ == "__main__":
    provider = LinkProvider()
    link = provider.link_for_klass(logging.LogRecord)
    print(link)

from __future__ import annotations

import functools

from importlib import metadata
import logging
import os
import sys

from mknodes.utils import helpers, inventorymanager


logger = logging.getLogger(__name__)

BUILTIN_URL = "https://docs.python.org/3/library/{mod}.html#{name}"


@functools.cache
def homepage_for_distro(dist_name: str) -> str | None:
    try:
        dist = metadata.distribution(dist_name)
    except metadata.PackageNotFoundError:
        return None
    else:
        return dist.metadata["Home-Page"]


class LinkProvider:
    def __init__(self):
        self.inv_manager = inventorymanager.InventoryManager()

    def add_inv_file(self, path: str | os.PathLike):
        self.inv_manager.add_inv_file(path)

    def link_for_klass(self, kls: type) -> str:
        module_path = kls.__module__
        kls_name = kls.__name__
        qual_name = kls.__qualname__.split("[")[0]  # to split off generics part
        if module_path == "builtins":
            url = BUILTIN_URL.format(mod="functions", name=kls_name)
            return helpers.linked(url, title=kls_name)
        if module_path in sys.stdlib_module_names:
            url = BUILTIN_URL.format(mod=module_path, name=f"{module_path}.{kls_name}")
            return helpers.linked(url, title=kls_name)
        module = module_path.split(".")[0]
        if url := homepage_for_distro(module):
            return helpers.linked(url, title=qual_name)
        return helpers.linked(qual_name)


if __name__ == "__main__":
    provider = LinkProvider()
    link = provider.link_for_klass(logging.LogRecord)
    print(link)

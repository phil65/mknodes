from __future__ import annotations

import functools

from importlib import metadata
import logging
import os

from mknodes.utils import helpers, inventorymanager


logger = logging.getLogger(__name__)


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
        qual_name = kls.__qualname__.split("[")[0]  # to split off generics part
        dotted_path = f"{module_path}.{qual_name}"
        if dotted_path in self.inv_manager:
            return self.inv_manager[dotted_path]
        module = module_path.split(".")[0]
        if url := homepage_for_distro(module):
            return helpers.linked(url, title=qual_name)
        return helpers.linked(qual_name)


if __name__ == "__main__":
    provider = LinkProvider()
    provider.add_inv_file("https://docs.python.org/3/objects.inv")
    link = provider.link_for_klass(logging.LogRecord)
    print(link)

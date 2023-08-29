from __future__ import annotations

import functools

from importlib import metadata
import logging
import os
import types

from mknodes import mkdocsconfig
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


def linked(identifier: str, title: str | None = None) -> str:
    suffix = "" if helpers.is_url(identifier) or identifier.endswith(".md") else ".md"
    return f"[{identifier if title is None else title}]({identifier}{suffix})"


class LinkProvider:
    def __init__(self, config=None):
        self.inv_manager = inventorymanager.InventoryManager()
        self.config = config or mkdocsconfig.load_config()

    def add_inv_file(self, path: str | os.PathLike):
        self.inv_manager.add_inv_file(path)

    def link_for_module(self, mod: types.ModuleType) -> str:
        dotted_path = mod.__name__
        if dotted_path in self.inv_manager:
            link = self.inv_manager[dotted_path]
            return linked(link, title=dotted_path)
        module = dotted_path.split(".")[0]
        if url := homepage_for_distro(module):
            return linked(url, title=mod.__name__)
        return linked(mod.__name__)

    def link_for_klass(self, kls: type) -> str:
        module_path = kls.__module__
        qual_name = kls.__qualname__.split("[")[0]  # to split off generics part
        dotted_path = f"{module_path}.{qual_name}"
        if dotted_path in self.inv_manager:
            link = self.inv_manager[dotted_path]
            return linked(link, title=qual_name)
        module = module_path.split(".")[0]
        if url := homepage_for_distro(module):
            return linked(url, title=qual_name)
        return linked(qual_name)

    def get_link(self, target) -> str:  # type: ignore[return]
        import mknodes

        base_url = self.config.site_url or ""
        match target:
            case mknodes.MkPage():
                path = target.resolved_file_path
                if self.config.use_directory_urls:
                    path = path.replace(".md", "/")
                else:
                    path = path.replace(".md", ".html")
                return base_url + path
            case mknodes.MkNav():
                if target.index_page:
                    path = target.index_page.resolved_file_path
                    if self.config.use_directory_urls:
                        path = path.replace(".md", "/")
                    else:
                        path = path.replace(".md", ".html")
                else:
                    path = target.resolved_file_path
                return base_url + path
            case str() if target.startswith("/"):
                return base_url.rstrip("/") + target
            case str() if helpers.is_url(target):
                return target
            case str():
                return f"{target}.md"
            case _:
                raise TypeError(target)


if __name__ == "__main__":
    provider = LinkProvider()
    provider.add_inv_file("https://docs.python.org/3/objects.inv")
    link = provider.link_for_klass(logging.LogRecord)
    print(link)

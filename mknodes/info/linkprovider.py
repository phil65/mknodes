from __future__ import annotations

from collections.abc import Sequence
from importlib import metadata
import os
import sys
import types

from typing import TYPE_CHECKING

from mknodes import paths
from mknodes.info import packageregistry
from mknodes.utils import helpers, inventorymanager, log


logger = log.get_logger(__name__)


if TYPE_CHECKING:
    import mknodes

    LinkableType = str | mknodes.MkPage | mknodes.MkNav | types.ModuleType | type
    """A type which can get linked by the LinkProvider."""


def homepage_for_distro(dist_name: str) -> str | None:
    """Return a link for given distribution from metadata.

    Used if no better link was found.

    Arguments:
        dist_name: Name of the distribution to get a link for
    """
    if dist_name in sys.stdlib_module_names:
        return None
    try:
        dist = packageregistry.get_info(dist_name)
    except metadata.PackageNotFoundError:
        logger.debug("Could not get package info for %s", dist_name)
        return None
    else:
        return dist.homepage


def linked(identifier: str, title: str | None = None) -> str:
    """Create a markdown link.

    Arguments:
        identifier: Target url
        title: Title to show as label
    """
    suffix = "" if helpers.is_url(identifier) or identifier.endswith(".md") else ".md"
    return f"[{identifier if title is None else title}]({identifier}{suffix})"


class LinkProvider:
    def __init__(
        self,
        base_url: str = "",
        use_directory_urls: bool = True,
        include_stdlib: bool = False,
    ):
        """Constructor.

        Arguments:
            base_url: Base URL of the website
            use_directory_urls: Use directory-style URLS
            include_stdlib: Load the stdlib inventory file on init
        """
        self.inv_manager = inventorymanager.InventoryManager()
        self.base_url = base_url
        self.excludes: set[str] = set()
        self.use_directory_urls = use_directory_urls
        if include_stdlib:
            self.add_inv_file(
                paths.RESOURCES / "python_objects.inv",
                base_url="https://docs.python.org/3/",
            )

    def set_excludes(self, excludes: Sequence[str]):
        """Set terms which should not get picked up by the linkprovider.

        That way handling of linking can be done by Markdown extensions.
        """
        self.excludes.update(excludes)

    def add_inv_file(self, path: str | os.PathLike, base_url: str | None = None):
        """Add an inventory file to the inventory manager.

        Arguments:
            path: Path or URL to the inventory file
            base_url: Base URL (required when inventory file is local)
        """
        self.inv_manager.add_inv_file(path, base_url=base_url)

    def url_for_module(
        self,
        mod: types.ModuleType,
        fallback_to_homepage: bool = True,
    ) -> str | None:
        """Return a url for given module.

        Arguments:
            mod: Module to get a url for
            fallback_to_homepage: Whether to get a link from Metadata if no other found
        """
        dotted_path = mod.__name__
        if dotted_path in self.inv_manager:
            return self.inv_manager[dotted_path]
        module = dotted_path.split(".")[0]
        return homepage_for_distro(module) if fallback_to_homepage else None

    def link_for_module(self, mod: types.ModuleType) -> str:
        """Return a markdown link for given module.

        Arguments:
            mod: Module to get a link for
        """
        dotted_path = mod.__name__
        fallback = dotted_path not in self.excludes
        if url := self.url_for_module(mod, fallback_to_homepage=fallback):
            return linked(url, dotted_path)
        return linked(dotted_path)

    def url_for_klass(
        self,
        kls: type,
        fallback_to_homepage: bool = True,
    ) -> str | None:
        """Return a url for given class.

        Arguments:
            kls: Klass to get a url for
            fallback_to_homepage: Whether to get a link from Metadata if no other found
        """
        module_path = kls.__module__
        qual_name = kls.__qualname__.split("[")[0]  # to split off generics part
        is_builtin = module_path == "builtins"
        dotted_path = qual_name if is_builtin else f"{module_path}.{qual_name}"
        if dotted_path in self.inv_manager:
            return self.inv_manager[dotted_path]
        module = module_path.split(".")[0]
        return homepage_for_distro(module) if fallback_to_homepage else None

    def link_for_klass(self, kls: type) -> str:
        """Return a markdown link for given class.

        Arguments:
            kls: Klass to get a link for
        """
        qual_name = kls.__qualname__.split("[")[0]  # to split off generics part
        fallback = qual_name not in self.excludes
        if url := self.url_for_klass(kls, fallback_to_homepage=fallback):
            return linked(url, qual_name)
        return linked(qual_name)

    def url_for_nav(self, nav: mknodes.MkNav) -> str:
        """Return the final URL for given MkNav.

        Arguments:
            nav: The Nav to link to
        """
        if nav.index_page:
            path = nav.index_page.resolved_file_path
            path = path.replace(".md", ".html")
        else:
            path = nav.resolved_file_path
        return self.base_url + path

    def url_for_page(self, page: mknodes.MkPage) -> str:
        """Return the final URL for given MkPage.

        Arguments:
            page: The Page to link to
        """
        path = page.resolved_file_path
        if self.use_directory_urls:
            path = path.replace(".md", "/")
        else:
            path = path.replace(".md", ".html")
        return self.base_url + path

    def get_link(self, target: LinkableType, title: str | None = None):
        """Return a markdown link for given target.

        Target can be a class, a module, a MkPage, MkNav or a string.

        Arguments:
            target: The thing to link to
            title: The title to use for the link
        """
        url = self.get_url(target)
        return linked(url, title)

    def get_url(self, target: LinkableType) -> str:  # type: ignore  # noqa: PLR0911
        """Get a url for given target.

        Target can be a class, a module, a MkPage, MkNav or a string.

        Arguments:
            target: The thing to link to
        """
        import mknodes

        match target:
            case mknodes.MkPage():
                return self.url_for_page(target)
            case mknodes.MkNav():
                return self.url_for_nav(target)
            case type():
                return self.url_for_klass(target) or ""
            case types.ModuleType():
                return self.url_for_module(target) or ""
            case str() if target.startswith("/"):
                return self.base_url.rstrip("/") + target
            case str() if helpers.is_url(target):
                return target
            case str() if target in mknodes.MkNode._name_registry:
                node = mknodes.MkNode.get_node(target)
                return self.get_url(node)
            case str():
                return f"{target}.md"
            case _:
                raise TypeError(target)


if __name__ == "__main__":
    provider = LinkProvider()
    provider.add_inv_file("https://docs.python.org/3/objects.inv")
    link = provider.link_for_klass(LinkProvider)
    print(link)

from __future__ import annotations

from git import TYPE_CHECKING

from mknodes.basenodes import mklink
from mknodes.navs import mknav
from mknodes.pages import mkpage


if TYPE_CHECKING:
    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink


class Navigation(dict):
    """An object representing MkDocs navigation."""

    def __setitem__(self, index: tuple | str, node: NavSubType):
        if isinstance(index, str):
            index = tuple(index.split("."))
        super().__setitem__(index, node)

    def __getitem__(self, index: tuple | str) -> NavSubType:
        if isinstance(index, str):
            index = tuple(index.split("."))
        return super().__getitem__(index)

    def __delitem__(self, index: tuple | str):
        if isinstance(index, str):
            index = tuple(index.split("."))
        super().__delitem__(index)

    def register(self, node: NavSubType):
        match node:
            case mknav.MkNav():
                self[(node.section,)] = node
            case mkpage.MkPage():
                self[node.path.removesuffix(".md")] = node
            case mklink.MkLink():
                self[node.title or node.url] = node
            case _:
                raise TypeError(node)

    @property
    def navs(self) -> list[mknav.MkNav]:
        """Return all registered navs."""
        return [node for node in self.values() if isinstance(node, mknav.MkNav)]

    @property
    def pages(self) -> list[mkpage.MkPage]:
        """Return all registered pages."""
        return [node for node in self.values() if isinstance(node, mkpage.MkPage)]

    @property
    def links(self) -> list[mklink.MkLink]:
        """Return all registered links."""
        return [node for node in self.values() if isinstance(node, mklink.MkLink)]

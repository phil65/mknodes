from __future__ import annotations

import pathlib

from git import TYPE_CHECKING

from mknodes.basenodes import mklink
from mknodes.navs import mknav, navbuilder
from mknodes.pages import mkpage


if TYPE_CHECKING:
    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink


class Navigation(dict):
    """An object representing MkDocs navigation."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_page: mkpage.MkPage | None = None
        self.index_title: str | None = None

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

    def to_literate_nav(self):
        nav = navbuilder.NavBuilder()
        # In a nav, the first inserted item becomes the index page in case
        # the section-index plugin is used, so we add it first.
        if self.index_page and self.index_title:
            nav[self.index_title] = pathlib.Path(self.index_page.path).as_posix()
        for path, item in self.items():
            if path is None:  # this check is just to make mypy happy
                continue
            match item:
                case mkpage.MkPage():
                    nav[path] = pathlib.Path(item.path).as_posix()
                case mknav.MkNav():
                    nav[path] = f"{item.section}/"
                case mklink.MkLink():
                    nav[path] = str(item.target)
                case _:
                    raise TypeError(item)
        return "".join(nav.build_literate_nav())

from __future__ import annotations

import pathlib

from git import TYPE_CHECKING

from mknodes.basenodes import mklink
from mknodes.navs import mknav, navbuilder
from mknodes.pages import mkpage


if TYPE_CHECKING:
    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink


class Navigation(dict):
    """An object representing A Website structure.

    The dict data consists of a mapping of a path-tuple -> NavSubType.
    It can contain navs, which in turn have their own navigation object.

    A special item is the index page. It can be accessed via the corresponding attributes.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index_page: mkpage.MkPage | None = None

    def __setitem__(self, index: tuple | str, node: NavSubType):
        """Put a Navigation-type instance into the registry.

        Index must be a unique path / title for this navigation object.
        If given a tuple, it is considered a nested path.
        """
        if isinstance(index, str):
            index = (index,)
        super().__setitem__(index, node)

    def __getitem__(self, index: tuple | str) -> NavSubType:
        if isinstance(index, str):
            index = (index,)
        return super().__getitem__(index)

    def __delitem__(self, index: tuple | str):
        if isinstance(index, str):
            index = (index,)
        super().__delitem__(index)

    def register(self, node: NavSubType):
        match node:
            case mknav.MkNav() | mkpage.MkPage() | mklink.MkLink():
                self[(node.title,)] = node
            case _:
                raise TypeError(node)

    @property
    def all_items(self) -> list[NavSubType]:
        nodes: list[NavSubType] = [self.index_page] if self.index_page else []
        nodes += list(self.values())
        return nodes

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

    def to_nav_dict(self) -> dict[str, str | dict]:
        """Return a nested dictionary ready to be used in the Mkocs nav section.

        The nav dict is a nested mapping describing the complete site navigation
        and contains all relative links to the markdown files of the pages
        as well as (external) URLs.

        """
        import mknodes as mk

        dct: dict[str, str | dict] = {}
        if idx := self.index_page:
            dct[idx.title] = pathlib.Path(idx.resolved_file_path).as_posix()
        for path, item in self.items():
            data = dct
            for part in path[:-1]:
                data = data.setdefault(part, {})
            match item:
                case mk.MkNav():
                    data[path[-1]] = item.nav.to_nav_dict()
                case mk.MkPage():
                    data[path[-1]] = item.resolved_file_path
                case mklink.MkLink():
                    data[path[-1]] = str(item.target)
        return dct

    def to_literate_nav(self) -> str:
        """Return a literate-nav-style str representation of the nav.

        Literate-Nav indexes equal to a (possibly nested) markdown link list.

        That markdown list only contains the direct child links of this nav, sub-navs
        are referenced to as subfolders.
        """
        nav = navbuilder.NavBuilder()
        if idx := self.index_page:
            nav[idx.title] = pathlib.Path(idx.path).as_posix()
        for path, item in self.items():
            if path is None:  # this check is just to make mypy happy
                continue
            match item:
                case mkpage.MkPage():
                    nav[path] = pathlib.Path(item.path).as_posix()
                case mknav.MkNav():
                    nav[path] = f"{item.title}/"
                case mklink.MkLink():
                    nav[path] = str(item.target)
                case _:
                    raise TypeError(item)
        return "".join(nav.build_literate_nav())


if __name__ == "__main__":
    import mknodes as mk

    nav_tree_path = pathlib.Path(__file__).parent.parent.parent / "tests/data/nav_tree/"
    nav_file = nav_tree_path / "SUMMARY.md"
    nav = mk.MkNav()
    nav.parse.file(nav_file)
    print(nav.nav.to_nav_dict())

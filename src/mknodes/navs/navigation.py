from __future__ import annotations

import concurrent.futures
import inspect
import pathlib
from typing import TYPE_CHECKING, Any

from anyenv import run_sync

from mknodes.basenodes import mklink
from mknodes.navs import navbuilder
from mknodes.pages import mkpage


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from mknodes.navs import mknav

    type NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink
    type PendingFn = Callable[[], None] | Callable[[], Awaitable[None]]


class Navigation:
    """An object representing a website structure.

    Contains a mapping of path-tuple -> NavSubType (navs, pages, links).
    Supports lazy execution of decorated route functions (sync and async).
    """

    def __init__(self, *, max_workers: int | None = None) -> None:
        self._data: dict[tuple[Any, ...], mknav.MkNav | mkpage.MkPage | mklink.MkLink] = {}
        self._index_page: mkpage.MkPage | None = None
        self._pending: list[PendingFn] = []
        self._materialized: bool = True
        self._max_workers: int | None = max_workers

    async def materialize(self) -> None:
        """Execute all pending route registrations (async)."""
        if self._materialized:
            return
        pending = self._pending
        self._pending = []
        self._materialized = True
        for fn in pending:
            result = fn()
            if inspect.iscoroutine(result):
                await result

    def _ensure_materialized(self) -> None:
        """Execute all pending route registrations."""
        if self._materialized:
            return
        pending = self._pending
        self._pending = []
        self._materialized = True

        def run_fn(fn: PendingFn) -> None:
            result = fn()
            if inspect.iscoroutine(result):
                run_sync(result)

        with concurrent.futures.ThreadPoolExecutor(max_workers=self._max_workers) as executor:
            futures = [executor.submit(run_fn, fn) for fn in pending]
            concurrent.futures.wait(futures)
            for future in futures:
                future.result()

    def add_pending(self, register_fn: PendingFn) -> None:
        """Add a pending registration to be executed lazily."""
        self._pending.append(register_fn)
        self._materialized = False

    @property
    def index_page(self) -> mkpage.MkPage | None:
        return self._index_page

    @index_page.setter
    def index_page(self, value: mkpage.MkPage | None) -> None:
        self._index_page = value

    def __setitem__(
        self,
        index: tuple[Any, ...] | str,
        node: mknav.MkNav | mkpage.MkPage | mklink.MkLink,
    ) -> None:
        """Put a Navigation-type instance into the registry."""
        if isinstance(index, str):
            index = (index,)
        self._data[index] = node

    def __getitem__(
        self, index: tuple[Any, ...] | str
    ) -> mknav.MkNav | mkpage.MkPage | mklink.MkLink:
        self._ensure_materialized()
        if isinstance(index, str):
            index = (index,)
        return self._data[index]

    def __delitem__(self, index: tuple[Any, ...] | str) -> None:
        self._ensure_materialized()
        if isinstance(index, str):
            index = (index,)
        del self._data[index]

    def __contains__(self, index: tuple[Any, ...] | str) -> bool:
        self._ensure_materialized()
        if isinstance(index, str):
            index = (index,)
        return index in self._data

    def __bool__(self) -> bool:
        self._ensure_materialized()
        return bool(self._data) or self._index_page is not None

    def register(self, node: mknav.MkNav | mkpage.MkPage | mklink.MkLink) -> None:
        from mknodes.navs import mknav as mknav_module

        match node:
            case mknav_module.MkNav() | mkpage.MkPage():
                self[node.title,] = node
            case _:
                raise TypeError(node)

    def get_all_items(self) -> list[mknav.MkNav | mkpage.MkPage | mklink.MkLink]:
        self._ensure_materialized()
        nodes: list[mknav.MkNav | mkpage.MkPage | mklink.MkLink] = (
            [self._index_page] if self._index_page else []
        )
        nodes += list(self._data.values())
        return nodes

    def get_navs(self) -> list[mknav.MkNav]:
        """Return all registered navs."""
        from mknodes.navs import mknav as mknav_module

        self._ensure_materialized()
        return [node for node in self._data.values() if isinstance(node, mknav_module.MkNav)]

    def get_pages(self) -> list[mkpage.MkPage]:
        """Return all registered pages."""
        self._ensure_materialized()
        return [node for node in self._data.values() if isinstance(node, mkpage.MkPage)]

    @property
    def links(self) -> list[mklink.MkLink]:
        """Return all registered links."""
        self._ensure_materialized()
        return [node for node in self._data.values() if isinstance(node, mklink.MkLink)]

    def to_nav_dict(self) -> dict[str, str | dict[str, Any]]:
        """Return a nested dictionary for the MkDocs nav section."""
        import mknodes as mk

        self._ensure_materialized()
        dct: dict[str, str | dict[str, Any]] = {}
        if idx := self._index_page:
            dct[idx.title] = pathlib.Path(idx.resolved_file_path).as_posix()
        for path, item in self._data.items():
            data = dct
            for part in path[:-1]:
                data = data.setdefault(part, {})  # type: ignore[assignment]  # pyright: ignore[reportUnknownMemberType, reportAttributeAccessIssue]
            assert isinstance(data, dict)
            match item:
                case mk.MkNav():
                    data[path[-1]] = item.nav.to_nav_dict()
                case mk.MkPage():
                    data[path[-1]] = item.resolved_file_path
                case mklink.MkLink():
                    data[path[-1]] = str(item.target)
        return dct

    def to_literate_nav(self) -> str:
        """Return a literate-nav-style str representation of the nav."""
        self._ensure_materialized()
        nav = navbuilder.NavBuilder()
        if idx := self._index_page:
            nav[idx.title] = pathlib.Path(idx.path).as_posix()
        for path, item in self._data.items():
            match item:
                case mkpage.MkPage():
                    nav[path] = pathlib.Path(item.path).as_posix()
                case _:
                    from mknodes.navs import mknav as mknav_module

                    if isinstance(item, mknav_module.MkNav):
                        nav[path] = f"{item.title}/"
                    elif isinstance(item, mklink.MkLink):
                        nav[path] = str(item.target)
                    else:
                        raise TypeError(item)
        return "".join(nav.build_literate_nav())


if __name__ == "__main__":
    import mknodes as mk

    nav_tree_path = pathlib.Path(__file__).parent.parent.parent / "tests/data/nav_tree/"
    nav_file = nav_tree_path / "SUMMARY.md"
    nav = mk.MkNav()
    nav.parse.file(nav_file)
    print(nav.nav.to_nav_dict())

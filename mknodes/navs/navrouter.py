from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mklink
from mknodes.navs import mknav
from mknodes.pages import mkpage
from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink
    PageCallable = Callable[[mkpage.MkPage], mkpage.MkPage | None]
    AsyncPageCallable = Callable[[mkpage.MkPage], Awaitable[mkpage.MkPage | None]]
    NavCallable = Callable[[mknav.MkNav], mknav.MkNav | None]
    AsyncNavCallable = Callable[[mknav.MkNav], Awaitable[mknav.MkNav | None]]
    NavSubTypeCallable = Callable[..., NavSubType]
    AsyncNavSubTypeCallable = Callable[..., Awaitable[NavSubType]]
    AnyPageCallable = PageCallable | AsyncPageCallable
    AnyNavCallable = NavCallable | AsyncNavCallable
    AnyNavSubTypeCallable = NavSubTypeCallable | AsyncNavSubTypeCallable

logger = log.get_logger(__name__)


class NavRouter:
    """Class used for MkNav decorator routing."""

    def __init__(self, nav: mknav.MkNav) -> None:
        """Constructor.

        Args:
            nav: MkNav to use for routing
        """
        self._nav = nav

    def __call__(self, *path: str) -> Callable[[AnyNavSubTypeCallable], Any]:
        """Decorator method to use for routing.

        The decorated functions need to return either a MkPage or an MkNav.
        They will get registered to the router-MkNav then.

        In comparison to `page()` and `nav()`, it is not required to know in advance what
        will be returned.

        Args:
            path: The section path for the returned `MkNav` / `MkPage`
        """

        def decorator(
            fn: AnyNavSubTypeCallable,
            path: tuple[str, ...] = path,
        ) -> AnyNavSubTypeCallable:
            async def register() -> None:
                result = fn()
                if inspect.iscoroutine(result):
                    node = await result
                else:
                    node = result
                node.parent = self._nav
                if isinstance(node, mkpage.MkPage):
                    node.created_by = fn
                elif isinstance(node, mknav.MkNav) and node.index_page:
                    node.index_page.created_by = fn
                self._nav.nav[path] = node

            self._nav.nav.add_pending(register)
            return fn

        return decorator

    def nav(self, *path: str, **kwargs: Any) -> Callable[[AnyNavCallable], Any]:
        """Decorator method to use for routing Navs.

        The decorated functions will get passed an MkNav as an argument which can be
        modified then.
        They will get registered to the router-MkNav afterwards.

        There is also the possibility to create a new MkNav and return it in the
        decorated method, that MkNav takes preference then over the modified one.

        Examples:
            ``` py
            @nav.route.nav("Routed nav")
            def _(nav: mk.MkNav):
                nav += ...
            ```

        Args:
            path: The section path for the returned MkNav
            kwargs: Keyword arguments passed to the MkNav constructor.
        """

        def decorator(
            fn: AnyNavCallable,
            path: tuple[str, ...] = path,
            kwargs: dict[str, Any] = kwargs,
        ) -> AnyNavCallable:
            async def register() -> None:
                node = mknav.MkNav(path[-1], parent=self._nav, **kwargs)
                result = fn(node)
                if inspect.iscoroutine(result):
                    awaited = await result
                    final = awaited or node
                else:
                    final = result or node
                final.parent = self._nav
                if final.index_page:
                    final.index_page.created_by = fn
                self._nav.nav[path] = final

            self._nav.nav.add_pending(register)
            return fn

        return decorator

    def page(self, *path: str, **kwargs: Any) -> Callable[[AnyPageCallable], Any]:
        """Decorator method to use for routing Pages.

        The decorated functions will get passed an MkPage as an argument which can be
        modified then.
        The resulting page will get registered to the router-MkNav afterwards.

        There is also the possibility to create a new MkPage and return it in the
        decorated method, that MkPage takes preference then over the modified one.

        The keyword arguments can be used to pass metadata-related keyword arguments
        to the MkPage constructor.

        Examples:
            ``` py
            @nav.route.page("Routed page", icon=...)
            def _(page: mk.MkPage):
                page += ...
            ```
        Args:
            path: The section path for the returned MkPage
            kwargs: Keyword arguments passed to the MkPage constructor.
        """

        def decorator(
            fn: AnyPageCallable,
            path: tuple[str, ...] = path,
            kwargs: dict[str, Any] = kwargs,
        ) -> AnyPageCallable:
            async def register() -> None:
                p = path[-1] if path else (self._nav.title or "Home")
                node = mkpage.MkPage(title=p, parent=self._nav, **kwargs)
                result = fn(node)
                if inspect.iscoroutine(result):
                    awaited = await result
                    final = awaited or node
                else:
                    final = result or node
                final.parent = self._nav
                final.created_by = fn
                self._nav.nav[path or self._nav.title or "Home"] = final

            self._nav.nav.add_pending(register)
            return fn

        return decorator

    def link(self, *path: str, url: str, title: str) -> None:
        link = mklink.MkLink(url, title)
        self._nav[path] = link


if __name__ == "__main__":
    nav = mknav.MkNav()
    router = NavRouter(nav)

    @router.page("Test")
    async def _(_page: mkpage.MkPage) -> None:
        pass

    print(nav.nav.get_pages())

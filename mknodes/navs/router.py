from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mklink
from mknodes.navs import mknav
from mknodes.pages import mkpage
from mknodes.utils import log


if TYPE_CHECKING:
    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink

logger = log.get_logger(__name__)


class Router:
    """Class used for MkNav decorator routing."""

    def __init__(self):
        self._page_registry = {}
        self._nav_registry = {}
        self._registry = {}

    def register_nodes(self, nav: mknav.MkNav):
        for path, fn in self._registry.items():
            node = fn()
            if fn.__name__ != "_":
                node._node_name = fn.__name__
            node.parent = nav
            if isinstance(node, mkpage.MkPage):
                node.created_by = fn
            elif isinstance(node, mknav.MkNav) and node.index_page:
                node.index_page.created_by = fn
            nav.nav[path] = node

        for path, (fn, kwargs, condition) in self._nav_registry.items():
            node = mknav.MkNav(path[-1], parent=nav, **kwargs)
            if condition and not condition(node):
                continue
            node = fn(node) or node
            if fn.__name__ != "_":
                node._node_name = fn.__name__
            node.parent = nav  # in case a new MkNav was generated
            if node.index_page:
                node.index_page.created_by = fn
            nav.nav[path] = node

        for path, (fn, kwargs, condition) in self._page_registry.items():
            p = path[-1] if path else (nav.title or "Home")
            node = mkpage.MkPage(title=p, parent=nav, **kwargs)
            if condition and not condition(node):
                continue
            node = fn(node) or node
            if fn.__name__ != "_":
                node._node_name = fn.__name__
            node.parent = nav  # in case a new MkPage was generated
            node.created_by = fn
            nav.nav[path or nav.title or "Home"] = node

    def route(
        self,
        *path: str,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing.

        The decorated functions need to return either a MkPage or an MkNav.
        They will get registered to the router-MkNav then.

        In comparison to `route_page()` and `route_nav()`, it is not required
         to know in advance what will be returned.

        Arguments:
            path: The section path for the returned `MkNav` / `MkPage`
        """

        def decorator(fn: Callable[..., NavSubType], path=path):
            self._registry[path] = fn
            return fn

        return decorator

    def route_nav(
        self,
        *path: str,
        condition: Callable | bool | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing Navs.

        The decorated functions will get passed an MkNav as an argument which can be
        modified then.
        They will get registered to the router-MkNav afterwards.

        There is also the possibility to create a new MkNav and return it in the
        decorated method, that MkNav takes preference then over the modified one.

        Examples:
            ``` py
            @router.route_nav("Routed nav")
            def _(nav: mk.MkNav):
                nav += ...
            ```

        Arguments:
            path: The section path for the returned MkNav
            condition: If passed, the nav is only included if the callable returns True
            kwargs: Keyword arguments passed to the MkNav constructor.
        """

        def decorator(
            fn: Callable[..., mknav.MkNav],
            path=path,
            kwargs=kwargs,
            condition=condition,
        ):
            if condition is not False:
                self._nav_registry[path] = (fn, kwargs, condition)
            return fn

        return decorator

    def route_page(
        self,
        *path: str,
        condition: Callable | bool | None = None,
        **kwargs: Any,
    ) -> Callable[[Callable], Callable]:
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
            @router.route_page("Routed page", icon=...)
            def _(page: mk.MkPage):
                page += ...
            ```
        Arguments:
            path: The section path for the returned MkPage
            condition: If passed, the page is only included if the callable returns True
            kwargs: Keyword arguments passed to the MkPage constructor.
        """

        def decorator(
            fn: Callable[..., mkpage.MkPage],
            path=path,
            kwargs=kwargs,
            condition=condition,
        ):
            if condition is not False:
                self._page_registry[path] = (fn, kwargs, condition)
            return fn

        return decorator


if __name__ == "__main__":
    nav = mknav.MkNav()
    router = Router()

    @router.route_page("Test")
    def _(page):
        pass

    router.register_nodes(nav)
    print(nav.nav.pages)

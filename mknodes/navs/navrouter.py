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


class NavRouter:
    """Class used for MkNav decorator routing."""

    def __init__(self, nav: mknav.MkNav):
        """Constructor.

        Arguments:
            nav: MkNav to use for routing
        """
        self._nav = nav

    def __call__(
        self,
        *path: str,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing.

        The decorated functions need to return either a MkPage or an MkNav.
        They will get registered to the router-MkNav then.

        In comparison to `page()` and `nav()`, it is not required to know in advance what
        will be returned.

        Arguments:
            path: The section path for the returned `MkNav` / `MkPage`
        """

        def decorator(fn: Callable[..., NavSubType], path=path) -> Callable:
            node = fn()
            node.parent = self._nav
            if isinstance(node, mkpage.MkPage):
                node.created_by = fn
            elif isinstance(node, mknav.MkNav) and node.index_page:
                node.index_page.created_by = fn
            self._nav.nav[path] = node
            return fn

        return decorator

    def nav(
        self,
        *path: str,
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
            @nav.route.nav("Routed nav")
            def _(nav: mk.MkNav):
                nav += ...
            ```

        Arguments:
            path: The section path for the returned MkNav
            kwargs: Keyword arguments passed to the MkNav constructor.
        """

        def decorator(
            fn: Callable[..., mknav.MkNav],
            path=path,
            kwargs=kwargs,
        ) -> Callable:
            node = mknav.MkNav(path[-1], parent=self._nav, **kwargs)
            node = fn(node) or node
            node.parent = self._nav  # in case a new MkPage was generated
            if node.index_page:
                node.index_page.created_by = fn
            self._nav.nav[path] = node
            return fn

        return decorator

    def page(
        self,
        *path: str,
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
            @nav.route.page("Routed page", icon=...)
            def _(page: mk.MkPage):
                page += ...
            ```
        Arguments:
            path: The section path for the returned MkPage
            kwargs: Keyword arguments passed to the MkPage constructor.
        """

        def decorator(
            fn: Callable[..., mkpage.MkPage],
            path=path,
            kwargs=kwargs,
        ) -> Callable:
            p = path[-1] if path else (self._nav.title or "Home")
            node = mkpage.MkPage(title=p, parent=self._nav, **kwargs)
            node = fn(node) or node
            node.parent = self._nav  # in case a new MkPage was generated
            node.created_by = fn
            self._nav.nav[path or self._nav.title or "Home"] = node
            return fn

        return decorator

    def link(self, *path: str, url: str, title: str):
        link = mklink.MkLink(url, title)
        self._nav[path] = link


if __name__ == "__main__":
    nav = mknav.MkNav()
    router = NavRouter(nav)

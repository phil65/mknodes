from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING

from mknodes.basenodes import mkadmonition, mkcode, mklink
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
        show_source: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing.

        The decorated functions need to return either a MkPage or an MkNav.
        They will get registered to the router-MkNav then.

        In comparison to `page()` and `nav()`, it is not required to know in advance what
        will be returned.


        Arguments:
            path: The section path for the returned `MkNav` / `MkPage`
            show_source: If True, a section containing the code will be inserted
                         at the start of the page (or index page if node is a Nav)
        """

        def decorator(fn: Callable[..., NavSubType], path=path) -> Callable:
            node = fn()
            node.parent = self._nav
            if show_source and isinstance(node, mkpage.MkPage):
                node.created_by = fn
                code = mkcode.MkCode.for_object(fn, header="Code for this page")
                code.parent = node
                node.items.insert(0, code)
            elif show_source and isinstance(node, mknav.MkNav) and node.index_page:
                code = mkcode.MkCode.for_object(fn)
                details = mkadmonition.MkAdmonition(
                    code,
                    title="Code for this section",
                    collapsible=True,
                    typ="quote",
                )
                details.parent = node.index_page
                node.index_page.items.append(details)
            self._nav.nav[path] = node
            return fn

        return decorator

    def nav(
        self,
        *path: str,
        show_source: bool = False,
        **kwargs,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing Navs.

        The decorated functions will get passed an MkNav as an argument which can be
        modified then.
        They will get registered to the router-MkNav afterwards.

        Arguments:
            path: The section path for the returned MkNav
            show_source: If True, a section containing the code will be inserted
                         at the end of the index page of the MkNav)
            kwargs: Keyword arguments passed to the MkNav constructor.
        """

        def decorator(
            fn: Callable[..., NavSubType],
            path=path,
            kwargs=kwargs,
        ) -> Callable:
            node = mknav.MkNav(path[-1], parent=self._nav, **kwargs)
            fn(node)
            if show_source and node.index_page:
                code = mkcode.MkCode.for_object(fn)
                details = mkadmonition.MkAdmonition(
                    code,
                    title="Code for this section",
                    collapsible=True,
                    typ="quote",
                )
                node.index_page.append(details)
            self._nav.nav[path] = node
            return fn

        return decorator

    def page(
        self,
        *path: str,
        show_source: bool = False,
        **kwargs,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing Pages.

        The decorated functions will get passed an MkPage as an argument which can be
        modified then.
        They will get registered to the router-MkNav afterwards.

        Arguments:
            path: The section path for the returned MkPage
            show_source: If True, a section containing the code will be inserted
                         at the end of the page
            kwargs: Keyword arguments passed to the MkPage constructor.
        """

        def decorator(
            fn: Callable[..., NavSubType],
            path=path,
            kwargs=kwargs,
        ) -> Callable:
            node = mkpage.MkPage(path[-1], parent=self._nav, **kwargs)
            fn(node)
            if show_source:
                node.created_by = fn
                code = mkcode.MkCode.for_object(fn)
                details = mkadmonition.MkAdmonition(
                    code,
                    title="Code for this page",
                    collapsible=True,
                    typ="quote",
                )
                node.append(details)
            self._nav.nav[path] = node
            return fn

        return decorator

    def link(self, *path: str, url: str, title: str):
        link = mklink.MkLink(url, title)
        self._nav[path] = link


if __name__ == "__main__":
    nav = mknav.MkNav()
    router = NavRouter(nav)

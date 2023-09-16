from __future__ import annotations

from collections.abc import Sequence
import pathlib
import types

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mklink, mknode
from mknodes.data.datatypes import PageStatusStr
from mknodes.navs import navbuilder, navparser, navrouter
from mknodes.pages import metadata, mkpage
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    from mknodes.navs import mkdoc, mknav
    from mknodes.pages import mkclasspage, mkmodulepage

    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink

logger = log.get_logger(__name__)


class MkNav(mknode.MkNode):
    """Nav section, representing a nestable menu.

    A nav is named (exception is the root nav, which has section name = None),
    has an associated virtual file (in general a SUMMARY.md),
    an optional index page and can contain other navs as well as pages.
    """

    ICON = "material/navigation-outline"
    REQUIRED_PLUGINS = ["literate_nav", "section_index"]

    def __init__(
        self,
        section: str | None = None,
        *,
        filename: str = "SUMMARY.md",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            section: Section name for the Nav
            filename: FileName for the resulting nav
            kwargs: Keyword arguments passed to parent
        """
        self.section = section  # helpers.slugify(section)
        self.filename = filename
        self.nav: dict[tuple | str | None, NavSubType] = {}
        self.route = navrouter.NavRouter(self)
        self.parse = navparser.NavParser(self)
        self.index_page: mkpage.MkPage | None = None
        self.index_title: str | None = None
        self.metadata = metadata.Metadata()
        super().__init__(**kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            section=self.section or "<root>",
            filename=self.filename,
        )

    def __setitem__(
        self,
        index: tuple | str,
        node: NavSubType,
    ):
        if isinstance(index, str):
            index = tuple(index.split("."))
        self.nav[index] = node

    def __getitem__(self, index: tuple | str) -> NavSubType:
        if isinstance(index, str):
            index = tuple(index.split("."))
        return self.nav[index]

    def __delitem__(self, index: tuple | str):
        if isinstance(index, str):
            index = tuple(index.split("."))
        del self.nav[index]

    def __add__(self, other: NavSubType):
        other.parent = self
        self._register(other)
        return self

    # def __len__(self):
    #     return len(self.nav) + (1 if self.index_page else 0)

    def __iter__(self):
        if self.index_page:
            yield self.index_page
        yield from self.nav.values()

    @property
    def path(self) -> str:
        """Get current path based on section / filename (usually section/SUMMARY.md)."""
        return (
            pathlib.Path(self.section) / self.filename
            if self.section
            else pathlib.Path(self.filename)
        ).as_posix()

    @property
    def metadata_file(self) -> str:
        """Get path to metadata file."""
        return (
            pathlib.Path(self.section) / ".meta.yml"
            if self.section
            else pathlib.Path(".meta.yml")
        ).as_posix()

    @property
    def resolved_file_path(self) -> str:
        """Returns the resulting section/subsection/../filename.xyz path."""
        path = "/".join(self.resolved_parts) + "/" + self.filename
        return path.lstrip("/")

    @property
    def navs(self) -> list[MkNav]:
        """Return all registered navs."""
        return [node for node in self.nav.values() if isinstance(node, MkNav)]

    @property
    def pages(self) -> list[mkpage.MkPage]:
        """Return all registered pages."""
        return [node for node in self.nav.values() if isinstance(node, mkpage.MkPage)]

    @property
    def links(self) -> list[mklink.MkLink]:
        """Return all registered links."""
        return [node for node in self.nav.values() if isinstance(node, mklink.MkLink)]

    @property
    def children(self):
        nodes: list[mknode.MkNode] = [self.index_page] if self.index_page else []
        nodes += list(self.nav.values())
        return nodes

    @children.setter
    def children(self, items):
        self.nav = dict(items)

    def add_nav(self, section: str) -> MkNav:
        """Create a Sub-Nav, register it to given Nav and return it.

        Arguments:
            section: Name of the new nav.
        """
        navi = MkNav(section=section, parent=self)
        self._register(navi)
        return navi

    def add_index_page(
        self,
        title: str | None = None,
        *,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        search_boost: float | None = None,
        exclude_from_search: bool | None = None,
        icon: str | None = None,
        status: PageStatusStr | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        path: str | None = None,
        template: str | None = None,
        tags: list[str] | None = None,
    ) -> mkpage.MkPage:
        """Register and return a index page with given title.

        Arguments:
            title: Title of the index page
            hide_toc: Hide table of contents
            hide_nav: Hide navigation menu
            hide_path: Hide breadcrumbs path
            search_boost: multiplier for search ranking
            exclude_from_search: Exclude page from search index
            icon: optional page icon
            status: Page status
            path: Optional path override
            description: Page description
            subtitle: Page subtitle
            template: Page template
            tags: tags to show above the main headline and within the search preview
        """
        page = mkpage.MkPage(
            path=path or "index.md",
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
            search_boost=search_boost,
            exclude_from_search=exclude_from_search,
            icon=icon,
            status=status,
            title=title,
            subtitle=subtitle,
            description=description,
            template=template,
            tags=tags,
            parent=self,
        )
        self.index_page = page
        self.index_title = title or self.section or "Home"
        return page

    def to_markdown(self) -> str:
        nav = navbuilder.NavBuilder()
        # In a nav, the first inserted item becomes the index page in case
        # the section-index plugin is used, so we add it first.
        if self.index_page and self.index_title:
            nav[self.index_title] = pathlib.Path(self.index_page.path).as_posix()
        for path, item in self.nav.items():
            if path is None:  # this check is just to make mypy happy
                continue
            match item:
                case mkpage.MkPage():
                    nav[path] = pathlib.Path(item.path).as_posix()
                case MkNav():
                    nav[path] = f"{item.section}/"
                case mklink.MkLink():
                    nav[path] = str(item.target)
                case _:
                    raise TypeError(item)
        return "".join(nav.build_literate_nav())

    def add_page(
        self,
        title: str | None = None,
        *,
        as_index: bool = False,
        path: str | None = None,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        search_boost: float | None = None,
        exclude_from_search: bool | None = None,
        icon: str | None = None,
        status: PageStatusStr | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        template: str | None = None,
        tags: list[str] | None = None,
    ) -> mkpage.MkPage:
        """Add a page to the Nav.

        Arguments:
            title: Page title
            as_index: Whether the page should become the index page.
            path: optional path override
            hide_toc: Hide table of contents
            hide_nav: Hide navigation menu
            hide_path: Hide breadcrumbs path
            search_boost: multiplier for search ranking
            exclude_from_search: Exclude page from search index
            icon: optional page icon
            status: Page status
            subtitle: Page subtitle
            description: Page description
            template: Page template
            tags: tags to show above the main headline and within the search preview
        """
        path = "index.md" if as_index else (path or f"{title}.md")
        page = mkpage.MkPage(
            title=title,
            path=path,
            parent=self,
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
            search_boost=search_boost,
            exclude_from_search=exclude_from_search,
            icon=icon,
            status=status,
            subtitle=subtitle,
            description=description,
            template=template,
            tags=tags,
        )
        if as_index:
            self.index_page = page
            self.index_title = title or self.section or "Home"
        else:
            self._register(page)
        return page

    def add_doc(
        self,
        module: types.ModuleType | Sequence[str] | str | None = None,
        *,
        filter_by___all__: bool = False,
        section_name: str | None = None,
        class_page: type[mkclasspage.MkClassPage] | None = None,
        module_page: type[mkmodulepage.MkModulePage] | None = None,
        flatten_nav: bool = False,
    ) -> mkdoc.MkDoc:
        """Add a module documentation to the Nav.

        Arguments:
            module: The module to create a documentation section for.
            filter_by___all__: Whether the documentation
            section_name: Override the name for the menu (default: module name)
            class_page: Override for the default ClassPage
            module_page: Override for the default ModulePage
            flatten_nav: Whether classes should be put into top-level of the nav
        """
        from mknodes.navs import mkdoc

        nav = mkdoc.MkDoc(
            module=module,
            filter_by___all__=filter_by___all__,
            parent=self,
            section_name=section_name,
            class_page=class_page,
            module_page=module_page,
            flatten_nav=flatten_nav,
        )
        self._register(nav)
        return nav

    def _register(self, node: NavSubType):
        match node:
            case MkNav():
                self.nav[(node.section,)] = node
            case mkpage.MkPage():
                self.nav[node.path.removesuffix(".md")] = node
            case mklink.MkLink():
                self.nav[node.title] = node
            case _:
                raise TypeError(node)

    @property
    def page_mapping(self):
        return {
            node.resolved_file_path: node
            for _level, node in self.iter_nodes()
            if hasattr(node, "resolved_file_path")
        }


if __name__ == "__main__":
    docs = MkNav()
    nav_tree_path = pathlib.Path(__file__).parent.parent.parent / "tests/data/nav_tree/"
    nav_file = nav_tree_path / "SUMMARY.md"
    nav = MkNav()
    nav.parse.file(nav_file)
    print(nav)

from __future__ import annotations

from collections.abc import Sequence
import pathlib
import types

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mknode
from mknodes.data.datatypes import PageStatusStr
from mknodes.navs import navigation, navparser, navrouter
from mknodes.pages import metadata, mkpage
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    from mknodes.navs import mkdoc
    from mknodes.pages import mkclasspage, mkmodulepage


logger = log.get_logger(__name__)


class MkNav(mknode.MkNode):
    """Nav section, representing a nestable menu.

    A nav is named (exception is the root nav, which has section name = None),
    has an associated virtual file (in general a SUMMARY.md),
    an optional index page and can contain other navs as well as pages and links.
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
        self.nav = navigation.Navigation()
        """Navigation object containing all child items."""
        self.route = navrouter.NavRouter(self)
        """Router used for decorator routing."""
        self.parse = navparser.NavParser(self)
        """Parser object used to build Navs from different data / directory structures."""
        self.metadata = metadata.Metadata()
        """Page Metadata, in form of a dataclass."""
        super().__init__(**kwargs)

    def __repr__(self):
        section = self.section or "<root>"
        return reprhelpers.get_repr(self, section=section, filename=self.filename)

    # The child items are managed by the Navigation object. We forward relevant calls
    # to the Navigation instance.

    def __setitem__(self, index: tuple | str, node: navigation.NavSubType):
        self.nav[index] = node

    def __getitem__(self, index: tuple | str) -> navigation.NavSubType:
        return self.nav[index]

    def __delitem__(self, index: tuple | str):
        del self.nav[index]

    # def __len__(self):
    #     return len(self.nav.all_items)

    def __iter__(self):
        yield from self.nav.all_items

    @property
    def index_page(self):
        return self.nav.index_page

    @index_page.setter
    def index_page(self, value):
        self.nav.index_page = value

    @property
    def index_title(self):
        return self.nav.index_title

    @index_title.setter
    def index_title(self, value):
        self.nav.index_title = value

    @property
    def children(self):
        return self.nav.all_items

    @children.setter
    def children(self, items):
        self.nav = navigation.Navigation(items)

    def __add__(self, other: navigation.NavSubType):
        """Use this to to register MkNodes."""
        other.parent = self
        self.nav.register(other)
        return self

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

    def add_nav(self, section: str) -> MkNav:
        """Create a Sub-Nav, register it to given Nav and return it.

        Arguments:
            section: Name of the new nav.
        """
        navi = MkNav(section=section, parent=self)
        self.nav.register(navi)
        return navi

    def add_index_page(
        self,
        title: str | None = None,
        *,
        hide: str | list[str] | None = None,
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
            hide: Hide parts of the website ("toc", "nav", "path")
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
            hide=hide,
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
        self.nav.index_page = page
        self.nav.index_title = title or self.section or "Home"
        return page

    def to_markdown(self) -> str:
        return self.nav.to_literate_nav()

    def add_page(
        self,
        title: str | None = None,
        *,
        as_index: bool = False,
        path: str | None = None,
        hide: list[str] | str | None = None,
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
            hide: Hide parts of the page ("toc", "nav", "path")
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
            hide=hide,
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
            self.nav.register(page)
        return page

    def add_doc(
        self,
        module: types.ModuleType | Sequence[str] | str | None = None,
        *,
        filter_by___all__: bool = False,
        section_name: str | None = None,
        class_page: type[mkclasspage.MkClassPage] | str | None = None,
        module_page: type[mkmodulepage.MkModulePage] | str | None = None,
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
        self.nav.register(nav)
        return nav


if __name__ == "__main__":
    docs = MkNav()
    nav_tree_path = pathlib.Path(__file__).parent.parent.parent / "tests/data/nav_tree/"
    nav_file = nav_tree_path / "SUMMARY.md"
    nav = MkNav()
    nav.parse.file(nav_file)
    print(nav)

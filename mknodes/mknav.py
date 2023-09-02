from __future__ import annotations

from collections.abc import Callable, Sequence
import itertools
import logging
import os
import pathlib
import re
import types

from typing import TYPE_CHECKING, Any, Self

from mknodes.basenodes import mkcode, mklink, mknode
from mknodes.data.datatypes import PageStatusStr
from mknodes.pages import metadata, mkpage
from mknodes.utils import navbuilder, reprhelpers


if TYPE_CHECKING:
    from mknodes import mkdoc, mknav
    from mknodes.pages import mkclasspage, mkmodulepage

    NavSubType = mknav.MkNav | mkpage.MkPage | mklink.MkLink

logger = logging.getLogger(__name__)

SECTION_AND_FILE_REGEX = r"^\* \[(.*)\]\((.*\.md)\)"
SECTION_AND_FOLDER_REGEX = r"^\* \[(.*)\]\((.*)\/\)"
SECTION_REGEX = r"^\* (.*)"


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
        append_markdown_to_pages: bool | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            section: Section name for the Nav
            filename: FileName for the resulting nav
            append_markdown_to_pages: Whether pages should contain a collapsible
                                      admonition containing the markup at the bottom.
                                      The setting will be used by all children
                                      and can be overridden by sub-navs or pages.
            kwargs: Keyword arguments passed to parent
        """
        self.section = section  # helpers.slugify(section)
        self.filename = filename
        self.nav: dict[tuple | str | None, NavSubType] = {}
        self.index_page: mkpage.MkPage | None = None
        self.index_title: str | None = None
        self.append_markdown_to_pages = append_markdown_to_pages
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
        nodes = [self.index_page] if self.index_page else []
        nodes += list(self.nav.values())
        return nodes

    @children.setter
    def children(self, items):
        self.nav = dict(items)

    def route(
        self,
        *path: str,
        show_source: bool = False,
    ) -> Callable[[Callable], Callable]:
        """Decorator method to use for routing.

        The decorated functions need to return either a MkPage or an MkNav.
        They will get registered to the router-MkNav then.

        Arguments:
            path: The section path for the returned MkNav / MkPage
            show_source: If True, a section containing the code will be inserted
                         at the start of the page (or index page if node is a Nav)
        """

        def decorator(fn: Callable[..., NavSubType], path=path) -> Callable:
            node = fn()
            node.parent = self
            if show_source and isinstance(node, mkpage.MkPage):
                code = mkcode.MkCode.for_object(fn, header="Code for this page")
                code.parent = node
                node.items.insert(0, code)
            elif show_source and isinstance(node, MkNav) and node.index_page:
                code = mkcode.MkCode.for_object(fn, header="Code for this section")
                code.parent = node.index_page
                node.index_page.items.insert(0, code)
            self.nav[path] = node
            return fn

        return decorator

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

    def virtual_files(self) -> dict[str, str | bytes]:
        """Override for MkNode.virtual_files."""
        dct = {self.path: self.to_markdown()}
        if self.metadata:
            dct[self.metadata_file] = str(self.metadata)
        return dct | super().virtual_files()

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
        from mknodes import mkdoc

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

    @classmethod
    def from_file(
        cls,
        path: str | os.PathLike,
        section: str | None = None,
        *,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        parent: MkNav | None = None,
    ) -> Self:
        """Load an existing SUMMARY.md style file.

        For each indentation level in SUMMARY.md, a new sub-nav is created.

        Should support all SUMMARY.md options except wildcards.

        Arguments:
            path: Path to the file
            section: Section name of new nav
            hide_toc: Hide table of contents for all pages
            hide_nav: Hide navigation menu for all pages
            hide_path: Hide breadcrumbs path for all pages
            parent: Optional parent item if the SUMMARY.md shouldnt be used as root nav.

        """
        path = pathlib.Path(path)
        if path.is_absolute():
            path = path.relative_to(pathlib.Path().absolute())
        content = path.read_text()
        return cls._from_text(
            content,
            section=section,
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
            parent=parent,
            path=path,
        )
        # max_indent = max(len(line) - len(line.lstrip()) for line in content.split("\n"))
        # content = [line.lstrip() for line in content.split("\n")]

    @classmethod
    def _from_text(
        cls,
        text: str,
        path: pathlib.Path,
        *,
        section: str | None = None,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        parent: MkNav | None = None,
    ) -> Self:
        """Create a nav based on a SUMMARY.md-style list, given as text.

        For each indentation level, a new sub-nav is created.

        Should support all SUMMARY.md options except wildcards.

        Arguments:
            text: Text to parse
            section: Section name for the nav
            hide_toc: Hide table of contents for all pages
            hide_nav: Hide navigation menu for all pages
            hide_path: Hide breadcrumbs path for all pages
            parent: Optional parent-nav in case the new nav shouldnt become the root nav.
            path: path of the file containing the text.
        """
        nav = cls(section, parent=parent)
        lines = text.split("\n")
        for i, line in enumerate(lines):
            # for first case we need to check whether following lines are indented.
            # If yes, then the path describes an index page.
            # * [Example](example_folder/sub_1.md)
            if match := re.match(SECTION_AND_FILE_REGEX, line):
                next_lines = lines[i + 1 :]
                if indented := list(
                    itertools.takewhile(lambda x: x.startswith("    "), next_lines),
                ):
                    unindented = "\n".join(j[4:] for j in indented)
                    subnav = MkNav._from_text(
                        unindented,
                        section=match[1],
                        hide_toc=hide_toc,
                        hide_nav=hide_nav,
                        hide_path=hide_path,
                        parent=nav,
                        path=path,
                    )
                    page = subnav.add_index_page(
                        hide_toc=hide_toc,
                        hide_nav=hide_nav,
                        hide_path=hide_path,
                    )
                    page += pathlib.Path(match[2]).read_text()
                    logger.info(
                        "Created subsection %s and loaded index page %s",
                        match[1],
                        match[2],
                    )
                    nav += subnav
                else:
                    page = mkpage.MkPage.from_file(
                        path=path.parent / match[2],
                        hide_toc=hide_toc,
                        hide_nav=hide_nav,
                        hide_path=hide_path,
                        parent=nav,
                    )
                    nav[match[1]] = page
                    logger.info("Created page %s from %s", match[1], match[2])
            # * [Example](example_folder/)
            elif match := re.match(SECTION_AND_FOLDER_REGEX, line):
                file_path = path.parent / f"{match[2]}/SUMMARY.md"
                subnav = MkNav.from_file(
                    file_path,
                    section=match[1],
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                )
                nav[match[1]] = subnav
                logger.info("Created subsection %s from %s", match[1], file_path)
            # * Example
            elif match := re.match(SECTION_REGEX, line):
                next_lines = lines[i + 1 :]
                indented = itertools.takewhile(lambda x: x.startswith("    "), next_lines)
                unindented = "\n".join(j[4:] for j in indented)
                subnav = MkNav._from_text(
                    unindented,
                    section=match[1],
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                    path=path,
                )
                logger.info("Created subsection %s from text", match[1])
                nav[match[1]] = subnav
        return nav

    @classmethod
    def from_folder(
        cls,
        folder: str | os.PathLike,
        *,
        recursive: bool = True,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        parent: MkNav | None = None,
    ) -> Self:
        """Load a MkNav tree from Folder.

        SUMMARY.mds are ignored.
        index.md files become index pages.

        To override the default behavior of using filenames as menu titles,
        the pages can set a title by using page metadata.

        Arguments:
            folder: Folder to load .md files from
            recursive: Whether all .md files should be included recursively.
            hide_toc: Whether to hide the toc for all pages
            hide_nav: Whether to hide the nav for all pages
            hide_path: Whether to hide the path for all pages
            parent: Optional parent-nav in case the new nav shouldnt become the root nav.
        """
        folder = pathlib.Path(folder)
        nav = cls(folder.name if parent else None, parent=parent)
        for path in folder.iterdir():
            if path.is_dir() and recursive and any(path.iterdir()):
                path = folder / path.parts[-1]
                subnav = cls.from_folder(
                    folder=path,
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                )
                nav += subnav
                logger.info("Loaded subnav from from %s", path)
            elif path.name == "index.md":
                page = mkpage.MkPage(
                    path=path.name,
                    content=path.read_text(),
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                )
                logger.info("Loaded index page from %s", path)
                nav.index_page = page
                nav.index_title = nav.section or "Home"
            elif path.suffix in [".md", ".html"] and path.name != "SUMMARY.md":
                page = mkpage.MkPage(
                    path=path.relative_to(folder),
                    content=path.read_text(),
                    hide_toc=hide_toc,
                    hide_nav=hide_nav,
                    hide_path=hide_path,
                    parent=nav,
                )
                nav += page
                logger.info("Loaded page from from %s", path)
        return nav


if __name__ == "__main__":
    docs = MkNav()
    nav_tree_path = pathlib.Path(__file__).parent.parent / "tests/data/nav_tree/"
    nav_file = nav_tree_path / "SUMMARY.md"
    nav = MkNav.from_file(nav_file)
    print(nav)

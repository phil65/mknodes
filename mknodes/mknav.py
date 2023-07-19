from __future__ import annotations

import logging
import os
import pathlib
import types

from typing import TYPE_CHECKING

import mkdocs_gen_files

from mknodes import mknav, mknode, mkpage, utils


if TYPE_CHECKING:
    from mknodes import mkdoc

logger = logging.getLogger(__name__)


class MkNav(mknode.MkNode):
    """Nav section, representing a nestable menu.

    A nav has a section name (exception can be the root), an associated virtual file
    (in general a SUMMARY.md) and can contain other navs as well as pages.

    Arguments:
        section: Section name for the Nav
        filename: FileName for the resulting nav
    """

    def __init__(
        self,
        section: str | os.PathLike | None = None,
        *,
        filename: str = "SUMMARY.md",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.section = str(section) if section else None
        self.filename = filename
        self.path = (
            pathlib.Path(section) / self.filename
            if section
            else pathlib.Path(self.filename)
        ).as_posix()
        self.nav: dict[tuple | str | None, mknav.MkNav | mkpage.MkPage] = {}
        # self._mapping = {}
        # self._editor = mkdocs_gen_files.editor.FilesEditor.current()
        # self._docs_dir = pathlib.Path(self._editor.config["docs_dir"])
        # self.files = self._editor.files

    def __repr__(self):
        return utils.get_repr(
            self,
            section=self.section or "<root>",
            filename=self.filename,
        )

    def __setitem__(self, item: tuple | str, node: mkpage.MkPage | MkNav):
        if isinstance(item, str):
            item = tuple(item.split("."))
        self.nav[item] = node

    def __getitem__(self, index: tuple) -> mkpage.MkPage | MkNav:
        return self.nav[index]

    @property
    def navs(self):
        return [node for node in self.nav.values() if isinstance(node, MkNav)]

    @property
    def pages(self):
        return [node for node in self.nav.values() if isinstance(node, mkpage.MkPage)]

    @property
    def children(self):
        return self.nav.values()

    @children.setter
    def children(self, items):
        self.nav = dict(items)

    def add_nav(self, section: str | os.PathLike) -> MkNav:
        """Create a Sub-Nav, register it to given Nav and return it.

        Arguments:
            section: Name of the new nav.
        """
        navi = mknav.MkNav(section=section, parent=self)
        self.nav[(section,)] = navi
        return navi

    def add_index_page(
        self,
        hide_toc: bool = False,
        hide_nav: bool = False,
    ) -> mkpage.MkPage:
        page = mkpage.MkPage(
            path="index.md", hide_toc=hide_toc, hide_nav=hide_nav, parent=self
        )
        self.nav[None] = page
        return page

    def write_navs(self):
        for navi in self.navs:
            navi.write()

    def virtual_files(self) -> dict[str, str]:
        return {str(self.path): self.to_markdown()}

    def to_markdown(self) -> str:
        nav = mkdocs_gen_files.Nav()
        for path, item in self.nav.items():
            # current approach: index pages have path = None, they dont become part
            # of the literate nav.
            # Not sure what`s best here, lot of combinations possible with
            # section-index etc.
            if path is None:
                continue
            match item:
                case mkpage.MkPage():
                    nav[path] = pathlib.Path(item.path).as_posix()
                case MkNav():
                    nav[path] = f"{item.section}/"
                case _:
                    raise TypeError(item)
        return "".join(nav.build_literate_nav())

    def add_page(
        self,
        title: str,
        *,
        hide_toc: bool = False,
        hide_nav: bool = False,
        hide_path: bool = False,
        filename: str | None = None,
    ) -> mkpage.MkPage:
        """Add a page to the Nav."""
        filename = filename or utils.slugify(f"{title}.md")
        page = mkpage.MkPage(
            path=filename,
            parent=self,
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
        )
        self.nav[title] = page
        return page

    def add_documentation(
        self,
        module: types.ModuleType | str,
        *,
        filter_by___all__: bool = False,
        section_name: str | None = None,
    ) -> mkdoc.MkDoc:
        """Add a module documentation to the Nav.

        Arguments:
            module: The module to create a documentation section for.
            filter_by___all__: Whether the documentation
            section_name: Override the name for the menu (default: module name)
        """
        from mknodes import mkdoc

        nav = mkdoc.MkDoc(
            module=module,
            filter_by___all__=filter_by___all__,
            parent=self,
            section_name=section_name,
        )
        self.nav[(nav.section,)] = nav
        return nav


if __name__ == "__main__":
    docs = MkNav()
    subnav = docs.add_nav("subnav")
    page = subnav.add_page("My first page!")
    page.add_admonition("Warning This is still beta", typ="danger", title="Warning!")
    page2 = subnav.add_page("And a second one")
    subsubnav = subnav.add_nav("SubSubNav")
    subsubnav = subsubnav.add_page("SubSubPage")
    from pprint import pprint

    pprint(docs.all_virtual_files())

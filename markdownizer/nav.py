from __future__ import annotations

import logging
import os
import pathlib
import types

from typing import TYPE_CHECKING

import mkdocs_gen_files

from markdownizer import markdownnode, mkpage, nav, utils


if TYPE_CHECKING:
    from markdownizer import moduledocumentation

logger = logging.getLogger(__name__)


class Nav(markdownnode.MarkdownNode):
    """Nav section, representing a nestable menu."""

    def __init__(
        self,
        section: str | os.PathLike | None = None,
        filename: str = "SUMMARY.md",
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.section = section
        self.filename = filename
        self.path = (
            pathlib.Path(section) / self.filename
            if section
            else pathlib.Path(self.filename)
        )
        self.nav = mkdocs_gen_files.Nav()
        # self._mapping = {}
        self.navs: list[nav.Nav] = []
        self.pages: list[mkpage.MkPage] = []
        # self._editor = mkdocs_gen_files.editor.FilesEditor.current()
        # self._docs_dir = pathlib.Path(self._editor.config["docs_dir"])
        # self.files = self._editor.files

    def __repr__(self):
        return utils.get_repr(
            self,
            section=self.section or "<root>",
            filename=self.filename,
        )

    def __setitem__(self, item: tuple | str, value: str | os.PathLike):
        if isinstance(item, str):
            item = tuple(item.split("."))
        self.nav[item] = pathlib.Path(value).as_posix()

    #     self._mapping[item] = value

    # def __getitem__(self, item):
    #     return self._mapping[item]

    @property
    def children(self):
        return self.pages + self.navs

    @children.setter
    def children(self, items):
        self.navs = [i for i in items if isinstance(i, Nav)]
        self.pages = [i for i in items if not isinstance(i, Nav)]

    def create_nav(self, section: str | os.PathLike) -> nav.Nav:
        navi = nav.Nav(section=section, parent=self)
        self.nav[(section,)] = f"{section}/"
        self.navs.append(navi)
        return navi

    def write_navs(self):
        for navi in self.navs:
            navi.write()

    def virtual_files(self):
        return {self.path: self.to_markdown()}

    def to_markdown(self):
        return "".join(self.nav.build_literate_nav())

    def create_page(self, title: str, **kwargs):
        filename = f"{title}.md"
        self.__setitem__(title, filename)
        page = mkpage.MkPage(path=filename, parent=self, **kwargs)
        self.pages.append(page)
        return page

    def create_documentation(
        self, module: types.ModuleType | str
    ) -> moduledocumentation.ModuleDocumentation:
        from markdownizer import moduledocumentation

        nav = moduledocumentation.ModuleDocumentation(module=module, parent=self)
        self.nav[(nav.module_name,)] = f"{nav.module_name}/"
        self.navs.append(nav)
        return nav


if __name__ == "__main__":
    docs = Nav()
    subnav = docs.create_nav("subnav")
    page = subnav.create_page("My first page!")
    page.add_admonition("Warning This is still beta", typ="danger", title="Warning!")
    page2 = subnav.create_page("And a second one")
    subsubnav = subnav.create_nav("SubSubNav")
    subsubnav = subsubnav.create_page("SubSubPage")
    from pprint import pprint

    pprint(docs.all_virtual_files())

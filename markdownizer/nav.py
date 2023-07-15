from __future__ import annotations

import logging
import os
import pathlib

import mkdocs_gen_files

from markdownizer import basesection, utils, nav, mkpage


logger = logging.getLogger(__name__)


class Nav(basesection.BaseSection):
    def __init__(
        self,
        section: str | os.PathLike,
        filename: str = "SUMMARY.md",
    ):
        super().__init__()
        self.section = section
        self.filename = filename
        self.path = pathlib.Path(section) / self.filename
        self.nav = mkdocs_gen_files.Nav()
        self.indentation = 0
        # self._mapping = {}
        self.navs = []
        self.pages = []

    def __repr__(self):
        return utils.get_repr(
            self,
            section=self.section,
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
        nav = nav.Nav(section=section, module_name=self.module_name)
        nav.parent_item = self
        self.nav[(section,)] = f"{section}/"
        self.navs.append(nav)
        return nav

    def write_navs(self):
        for nav in self.navs:
            nav.write()

    def virtual_files(self):
        return {self.path: self.to_markdown()}

    def to_markdown(self):
        return "".join(self.nav.build_literate_nav())

    def add_document(self, nav_path: str | tuple, file_path: os.PathLike | str, **kwargs):
        self.__setitem__(nav_path, file_path)
        page = mkpage.MkPage(**kwargs)
        self.pages.append(page)
        return page


if __name__ == "__main__":
    nav = Nav(section="prettyqt")
    nav.nav["test"] = "t/"
    print(nav)

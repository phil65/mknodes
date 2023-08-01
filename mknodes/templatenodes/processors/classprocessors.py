from __future__ import annotations

import logging

from mknodes import mkpage
from mknodes.basenodes import mkdocstrings
from mknodes.templatenodes import mkclassdiagram, mkclasstable


logger = logging.getLogger(__name__)


class ClassPageProcessor:
    ID: str

    def __init__(self, klass: type, parts=None, header: str | None = None):
        self.klass = klass
        self.parts = parts or klass.__module__.split(".")
        self.header = header

    def get_header(self, page: mkpage.MkPage):
        return self.header if self.header is not None else self.get_default_header(page)

    def check_if_apply(self, page: mkpage.MkPage):
        return True

    def append_section(self, page: mkpage.MkPage):
        return NotImplementedError

    def get_default_header(self, page: mkpage.MkPage):
        return NotImplementedError


class BaseClassTablePageProcessor(ClassPageProcessor):
    ID = "baseclass_table"

    def append_section(self, page: mkpage.MkPage):
        bases = list(self.klass.__bases__)
        table = mkclasstable.MkClassTable(bases)
        page += table

    def check_if_apply(self, page: mkpage.MkPage):
        return len(self.klass.mro()) > 2  # noqa: PLR2004

    def get_default_header(self, page: mkpage.MkPage):
        return "Base classes"


class SubClassTablePageProcessor(ClassPageProcessor):
    ID = "subclass_table"

    def append_section(self, page):
        table = mkclasstable.MkClassTable(self.klass.__subclasses__(), layout="compact")
        page += table

    def check_if_apply(self, page: mkpage.MkPage):
        return len(self.klass.__subclasses__()) > 0

    def get_default_header(self, page: mkpage.MkPage):
        return "Subclasses"


class InheritanceDiagramPageProcessor(ClassPageProcessor):
    ID = "inheritance_diagram"

    def append_section(self, page: mkpage.MkPage):
        diagram = mkclassdiagram.MkClassDiagram(self.klass, mode="parent_tree")
        page += diagram

    def get_default_header(self, page: mkpage.MkPage):
        return "⋔ Inheritance diagram"


class MkDocStringPageProcessor(ClassPageProcessor):
    ID = "docstrings"

    def append_section(self, page: mkpage.MkPage):
        module_path = ".".join(self.parts).rstrip(".")
        path = f"{module_path}.{self.klass.__name__}"
        diagram = mkdocstrings.MkDocStrings(path, show_root_toc_entry=False)
        page += diagram

    def get_default_header(self, page: mkpage.MkPage):
        return "🛈 DocStrings"


if __name__ == "__main__":
    page = mkpage.MkPage()
    processor = BaseClassTablePageProcessor(mkpage.MkPage)
    processor.append_section(page)
    print(page)

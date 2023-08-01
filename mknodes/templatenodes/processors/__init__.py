from __future__ import annotations

import logging

from mknodes import mkpage
from mknodes.basenodes import mkdocstrings
from mknodes.templatenodes import mkclassdiagram, mkclasstable
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class PageProcessor:
    ID: str

    def __init__(self, item, *, header: str | None = None):
        self.item = item
        self.header = header

    def get_header(self, page: mkpage.MkPage):
        return self.header if self.header is not None else self.get_default_header(page)

    def check_if_apply(self, page: mkpage.MkPage):
        return True

    def append_section(self, page: mkpage.MkPage):
        return NotImplementedError

    def get_default_header(self, page: mkpage.MkPage):
        return NotImplementedError


class BaseClassTablePageProcessor(PageProcessor):
    ID = "baseclass_table"

    def append_section(self, page: mkpage.MkPage):
        bases = list(self.item.__bases__)
        table = mkclasstable.MkClassTable(bases)
        page += table

    def check_if_apply(self, page: mkpage.MkPage):
        return len(self.item.mro()) > 2  # noqa: PLR2004

    def get_default_header(self, page: mkpage.MkPage):
        return "Base classes"


class SubClassTablePageProcessor(PageProcessor):
    ID = "subclass_table"

    def append_section(self, page):
        table = mkclasstable.MkClassTable(self.item.__subclasses__(), layout="compact")
        page += table

    def check_if_apply(self, page: mkpage.MkPage):
        return len(self.item.__subclasses__()) > 0

    def get_default_header(self, page: mkpage.MkPage):
        return "Subclasses"


class InheritanceDiagramPageProcessor(PageProcessor):
    ID = "inheritance_diagram"

    def append_section(self, page: mkpage.MkPage):
        diagram = mkclassdiagram.MkClassDiagram(self.item, mode="parent_tree")
        page += diagram

    def get_default_header(self, page: mkpage.MkPage):
        return "⋔ Inheritance diagram"


class MkDocStringPageProcessor(PageProcessor):
    ID = "docstrings"

    def append_section(self, page: mkpage.MkPage):
        path = classhelpers.to_dotted_path(self.item)
        diagram = mkdocstrings.MkDocStrings(path, show_root_toc_entry=False)
        page += diagram

    def get_default_header(self, page: mkpage.MkPage):
        return "🛈 DocStrings"


class DocPageProcessor(PageProcessor):
    ID = "doc"

    def append_section(self, page: mkpage.MkPage):
        page += helpers.get_doc(self.item)

    def get_default_header(self, page: mkpage.MkPage):
        return "Docs"

    def check_if_apply(self, page: mkpage.MkPage):
        return bool(self.item.__doc__)


if __name__ == "__main__":
    page = mkpage.MkPage()
    processor = BaseClassTablePageProcessor(mkpage.MkPage)
    processor.append_section(page)
    print(page)

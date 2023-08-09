from __future__ import annotations

import logging

from mknodes.pages import mkpage
from mknodes.basenodes import mkdocstrings, mkheader
from mknodes.templatenodes import mkclassdiagram, mkclasstable
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class PageProcessor:
    ID: str

    def __init__(self, item, *, header: str | None = None):
        self.item = item
        self.header = header

    def get_header(self, page: mkpage.MkPage):
        """Returns either default header or an override."""
        return self.header if self.header is not None else self.get_default_header(page)

    def append_section(self, page: mkpage.MkPage):
        """Adds the block together with a header to the page."""
        if header := self.get_header(page):
            page += mkheader.MkHeader(header)
        self.append_block(page)

    def check_if_apply(self, page: mkpage.MkPage):
        """Re-implement this if the section should only conditionally be added."""
        return True

    def append_block(self, page: mkpage.MkPage):
        """Re-implement this and attach your stuff to given page."""
        raise NotImplementedError

    def get_default_header(self, page: mkpage.MkPage) -> str | None:
        """Re-implement this and return the default section header."""
        return None


class StaticBlockProcessor(PageProcessor):
    def append_block(self, page: mkpage.MkPage):
        page += self.item

    def get_header(self, page):
        return None


class ClassTablePageProcessor(PageProcessor):
    ID = "baseclass_table"

    def append_block(self, page: mkpage.MkPage):
        table = mkclasstable.MkClassTable(self.item)
        page += table

    def get_default_header(self, page: mkpage.MkPage):
        return "Classes"


class BaseClassTablePageProcessor(PageProcessor):
    ID = "baseclass_table"

    def append_block(self, page: mkpage.MkPage):
        bases = list(self.item.__bases__)
        table = mkclasstable.MkClassTable(bases)
        page += table

    def check_if_apply(self, page: mkpage.MkPage):
        return len(self.item.mro()) > 2  # noqa: PLR2004

    def get_default_header(self, page: mkpage.MkPage):
        return "Base classes"


class SubClassTablePageProcessor(PageProcessor):
    ID = "subclass_table"

    def append_block(self, page):
        subclasses = list(classhelpers.iter_subclasses(self.item, recursive=False))
        table = mkclasstable.MkClassTable(subclasses, layout="compact")
        page += table

    def check_if_apply(self, page: mkpage.MkPage):
        subclasses = list(classhelpers.iter_subclasses(self.item, recursive=False))
        return len(subclasses) > 0

    def get_default_header(self, page: mkpage.MkPage):
        return "Subclasses"


class InheritanceDiagramPageProcessor(PageProcessor):
    ID = "inheritance_diagram"

    def append_block(self, page: mkpage.MkPage):
        diagram = mkclassdiagram.MkClassDiagram(self.item, mode="baseclasses")
        page += diagram

    def get_default_header(self, page: mkpage.MkPage):
        return "⋔ Inheritance diagram"


class MkDocStringPageProcessor(PageProcessor):
    ID = "docstrings"

    def append_block(self, page: mkpage.MkPage):
        path = classhelpers.to_dotted_path(self.item)
        diagram = mkdocstrings.MkDocStrings(path, show_root_toc_entry=False)
        page += diagram

    def get_default_header(self, page: mkpage.MkPage):
        return "🛈 DocStrings"


class DocPageProcessor(PageProcessor):
    ID = "doc"

    def append_block(self, page: mkpage.MkPage):
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

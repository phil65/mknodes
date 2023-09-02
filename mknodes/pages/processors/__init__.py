from __future__ import annotations

import logging

from mknodes.basenodes import mkcontainer, _mkdocstrings, mkheader
from mknodes.templatenodes import mkclassdiagram, mkclasstable, mkmoduletable
from mknodes.utils import classhelpers, inspecthelpers


logger = logging.getLogger(__name__)


class ContainerProcessor:
    ID: str

    def __init__(self, item, *, header: str | None = None):
        self.item = item
        self.header = header

    def get_header(self, node: mkcontainer.MkContainer):
        """Returns either default header or an override."""
        return self.header if self.header is not None else self.get_default_header(node)

    def append_section(self, node: mkcontainer.MkContainer):
        """Adds the block together with a header to the node."""
        if header := self.get_header(node):
            node += mkheader.MkHeader(header)
        self.append_block(node)

    def check_if_apply(self, node: mkcontainer.MkContainer):
        """Re-implement this if the section should only conditionally be added."""
        return True

    def append_block(self, node: mkcontainer.MkContainer):
        """Re-implement this and attach your stuff to given node."""
        raise NotImplementedError

    def get_default_header(self, node: mkcontainer.MkContainer) -> str | None:
        """Re-implement this and return the default section header."""
        return None


class StaticBlockProcessor(ContainerProcessor):
    ID = "static"

    def append_block(self, node: mkcontainer.MkContainer):
        node += self.item

    def get_header(self, node):
        return None


class ModuleTableContainerProcessor(ContainerProcessor):
    ID = "module_table"

    def append_block(self, node: mkcontainer.MkContainer):
        modules = classhelpers.get_submodules(self.item)
        table = mkmoduletable.MkModuleTable(modules)
        node += table

    def check_if_apply(self, node: mkcontainer.MkContainer):
        return bool(classhelpers.get_submodules(self.item))

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "Modules"


class ClassTableContainerProcessor(ContainerProcessor):
    ID = "baseclass_table"

    def append_block(self, node: mkcontainer.MkContainer):
        table = mkclasstable.MkClassTable(self.item)
        node += table

    def check_if_apply(self, node: mkcontainer.MkContainer):
        return bool(self.item)

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "Classes"


class BaseClassTableContainerProcessor(ContainerProcessor):
    ID = "baseclass_table"

    def append_block(self, node: mkcontainer.MkContainer):
        bases = list(self.item.__bases__)
        table = mkclasstable.MkClassTable(bases)
        node += table

    def check_if_apply(self, node: mkcontainer.MkContainer):
        try:
            return len(self.item.mro()) > 2  # noqa: PLR2004
        except TypeError:
            return False

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "Base classes"


class SubClassTableContainerProcessor(ContainerProcessor):
    ID = "subclass_table"

    def append_block(self, node):
        subclasses = list(classhelpers.iter_subclasses(self.item, recursive=False))
        table = mkclasstable.MkClassTable(subclasses, layout="compact")
        node += table

    def check_if_apply(self, node: mkcontainer.MkContainer):
        subclasses = list(classhelpers.iter_subclasses(self.item, recursive=False))
        return len(subclasses) > 0

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "Subclasses"


class InheritanceDiagramContainerProcessor(ContainerProcessor):
    ID = "inheritance_diagram"

    def append_block(self, node: mkcontainer.MkContainer):
        diagram = mkclassdiagram.MkClassDiagram(self.item, mode="baseclasses")
        node += diagram

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "⋔ Inheritance diagram"


class MkDocStringContainerProcessor(ContainerProcessor):
    ID = "docstrings"

    def append_block(self, node: mkcontainer.MkContainer):
        path = classhelpers.to_dotted_path(self.item)
        diagram = _mkdocstrings.MkDocStrings(path, show_root_toc_entry=False)
        node += diagram

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "🛈 DocStrings"


class DocContainerProcessor(ContainerProcessor):
    ID = "doc"

    def append_block(self, node: mkcontainer.MkContainer):
        node += inspecthelpers.get_doc(self.item)

    def get_default_header(self, node: mkcontainer.MkContainer):
        return "Docs"

    def check_if_apply(self, node: mkcontainer.MkContainer):
        return bool(self.item.__doc__)


if __name__ == "__main__":
    node = mkcontainer.MkContainer()
    processor = BaseClassTableContainerProcessor(mkcontainer.MkContainer)
    processor.append_section(node)
    print(node)

from __future__ import annotations

import logging
import sys

from .basesection import BaseSection, Code, Text
from .admonition import Admonition
from .docstrings import DocStrings
from .image import BinaryImage, Image
from .list import List
from .mermaiddiagram import MermaidDiagram
from .table import Table
from .mkpage import ClassPage, MkPage, ModulePage
from .nav import Nav
from .moduledocumentation import ModuleDocumentation
from .docs import Docs

__all__ = [
    "BaseSection",
    "Docs",
    "Nav",
    "DocStrings",
    "Text",
    "Code",
    "Image",
    "BinaryImage",
    "MkPage",
    "Admonition",
    "MermaidDiagram",
    "Table",
    "List",
    "ClassPage",
    "ModulePage",
    "ModuleDocumentation",
]

__version__ = "0.0.1"

logger = logging.getLogger(__name__)



if __name__ == "__main__":
    from prettyqt import core
    from prettyqt.utils import helpers

    doc = Page([], True, True)
    doc += Admonition("info", "etst")
    doc += Table(data=dict(a=[1, 2], b=["c", "D"]), header="From mapping")
    doc += PropertyTable(core.StringListModel)
    doc += DocStrings(helpers, header="DocStrings")
    doc += DependencyTable("prettyqt")
    doc += MermaidDiagram.for_classes([Table], header="Mermaid diagram")
    from fsspec import AbstractFileSystem

    print(link_for_class(AbstractFileSystem))

    # print(doc.to_markdown())
    # print(text)

from __future__ import annotations

import logging
import os
import pathlib

from typing import Any

from mknodes import (
    classdiagram,
    classhelpers,
    classtable,
    docstrings,
    mkpage,
    utils,
)


logger = logging.getLogger(__name__)


class ClassPage(mkpage.MkPage):
    """Page showing information about a class.

    Arguments:
        klass: class to show info for
        module_path: If given, overrides module returned by class.__module__
                     This can be useful if you want to link to an aliased class
                     (for example a class imported to __init__.py)
        path: some path for the file.
        kwargs: keyword arguments passed to base class
    """

    def __init__(
        self,
        klass: type,
        *,
        module_path: tuple[str, ...] | str | None = None,
        hide_toc: bool = False,
        hide_nav: bool = False,
        hide_path: bool = False,
        path: str | os.PathLike = "",
        **kwargs: Any,
    ):
        # TODO: should path be settable?
        path = pathlib.Path(f"{klass.__name__}.md")
        super().__init__(
            path=path,
            hide_toc=hide_toc,
            hide_nav=hide_nav,
            hide_path=hide_path,
            **kwargs,
        )
        self.klass = klass
        match module_path:
            case None:
                self.parts = klass.__module__.split(".")
            case _:
                self.parts = classhelpers.to_module_parts(module_path)
        self._build()

    def __repr__(self):
        return utils.get_repr(self, klass=self.klass, path=str(self.path))

    @staticmethod
    def examples():
        yield dict(klass=ClassPage)

    def add_class_diagram(self, mode: classdiagram.DiagramModeStr = "parent_tree"):
        diagram = classdiagram.ClassDiagram(self.klass, mode=mode)
        self.append(diagram)
        return diagram

    def _build(self):
        module_path = ".".join(self.parts).rstrip(".")
        path = f"{module_path}.{self.klass.__name__}"
        item = docstrings.DocStrings(path, header="DocStrings")
        self.append(item)
        if tbl := classtable.ClassTable(self.klass):
            self.append(tbl)
        item = classdiagram.ClassDiagram(self.klass, header="Inheritance diagram")
        self.append(item)


if __name__ == "__main__":
    doc = ClassPage(ClassPage)
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

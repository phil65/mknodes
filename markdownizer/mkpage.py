from __future__ import annotations

import logging
import os
import pathlib
import types

from markdownizer import (
    basesection,
    classhelpers,
    docstrings,
    mermaiddiagram,
    table,
    utils,
)


logger = logging.getLogger(__name__)

HEADER = "---\n{options}\n---\n\n"


class MkPage(basesection.BaseSection):
    def __init__(
        self,
        items: list | None = None,
        hide_toc: bool = False,
        hide_nav: bool = False,
        hide_path: bool = False,
        path: str | os.PathLike = "",
        parent=None,
    ):
        super().__init__(parent=parent)
        self.items = items or []
        self.path = path
        self.header_options = {}
        if hide_toc:
            self.header_options.setdefault("hide", []).append("toc")
        if hide_nav:
            self.header_options.setdefault("hide", []).append("nav")
        if hide_path:
            self.header_options.setdefault("hide", []).append("path")

    def __repr__(self):
        return utils.get_repr(self, path=str(self.path))

    def __add__(self, other):
        self.append(other)
        return self

    def __iter__(self):
        return iter(self.items)

    def __str__(self):
        return self.to_markdown()

    @property
    def children(self):
        return self.items

    @children.setter
    def children(self, children):
        self.items = children

    def virtual_files(self):
        return {self.path: self.to_markdown()}

    def to_markdown(self) -> str:
        header = self.get_header()
        content_str = "\n\n".join(i.to_markdown() for i in self.items)
        return header + content_str if header else content_str

    def get_header(self) -> str:
        lines = []
        keys = self.header_options.keys()
        if not keys:
            return ""
        for option in keys:
            lines.append(f"{option}:")
            lines.extend(f"  - {area}" for area in self.header_options[option])
        return HEADER.format(options="\n".join(lines))

    def append(self, other: str | basesection.BaseSection):
        if isinstance(other, str):
            other = basesection.Text(other)
        other.parent_item = self
        self.items.append(other)


class ClassPage(MkPage):
    def __init__(
        self,
        klass: type,
        module_path: tuple[str, ...] | str | None = None,
        path: str | os.PathLike = "",
        **kwargs,
    ):
        """Document showing info about a class.

        Arguments:
            klass: class to show info for
            module_path: If given, overrides module returned by class.__module__
                         This can be useful if you want to link to an aliased class
                         (for example a class imported to __init__.py)
            path: some path for the file.
            kwargs: keyword arguments passed to base class
        """
        path = pathlib.Path(path).with_name(f"{klass.__name__}.md")
        super().__init__(path=path, **kwargs)
        self.klass = klass
        match module_path:
            case None:
                self.parts = klass.__module__.split(".")
            case _:
                self.parts = classhelpers.to_module_parts(module_path)
        self._build()

    def _build(self):
        module_path = ".".join(self.parts).rstrip(".")
        self.append(
            docstrings.DocStrings(
                f"{module_path}.{self.klass.__name__}", header="DocStrings"
            ),
        )
        if tbl := table.Table.get_ancestor_table_for_klass(self.klass):
            self.append(tbl)
        self.append(
            mermaiddiagram.MermaidDiagram.for_classes(
                [self.klass], header="Inheritance diagram"
            ),
        )
        # self.append(mermaiddiagram.MermaidDiagram.for_subclasses([self.klass]))


class ModulePage(MkPage):
    """Document showing info about a module.

    Arguments:
        module: ModuleType or path to model to show info for.
        module: Some path for the file.
        docstrings: Whether to show docstrings for given module.
        show_class_table: ModuleType or path to model to show info for.
    """

    def __init__(
        self,
        module: tuple[str, ...] | str | types.ModuleType,
        path: str | os.PathLike = "",
        *,
        docstrings: bool = False,
        show_class_table: bool = True,
        **kwargs,
    ):
        path = pathlib.Path(path).with_name("index.md")
        super().__init__(path=path, **kwargs)
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(self.parts)
        self.docstrings = docstrings
        self.show_class_table = show_class_table
        self._build()

    def _build(self):
        if doc := self.module.__doc__:
            self.append(doc)
        if self.docstrings:
            self.append(docstrings.DocStrings(f'{".".join(self.parts)}'))
        if self.show_class_table:
            klasses = list(
                classhelpers.iter_classes_for_module(
                    self.parts, module_filter=self.parts[0]
                )
            )
            self.append(table.Table.get_classes_table(klasses))


if __name__ == "__main__":
    doc = MkPage()
    # print(doc.children)

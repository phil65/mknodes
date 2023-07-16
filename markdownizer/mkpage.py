from __future__ import annotations

import logging
import os
import pathlib
import types

from typing import Any

from markdownizer import (
    admonition,
    classhelpers,
    classtable,
    code as codeblock,
    docstrings,
    markdownnode,
    mermaiddiagram,
    nav,
    utils,
)


logger = logging.getLogger(__name__)

HEADER = "---\n{options}\n---\n\n"


class MkPage(markdownnode.MarkdownContainer):
    def __init__(
        self,
        hide_toc: bool = False,
        hide_nav: bool = False,
        hide_path: bool = False,
        path: str | os.PathLike = "",
        parent: nav.Nav | None = None,
        **kwargs: Any,
    ):
        super().__init__(parent=parent, **kwargs)
        self.path = path
        self.header_options: dict[str, Any] = {}
        if hide_toc:
            self.header_options.setdefault("hide", []).append("toc")
        if hide_nav:
            self.header_options.setdefault("hide", []).append("nav")
        if hide_path:
            self.header_options.setdefault("hide", []).append("path")

    def __repr__(self):
        return utils.get_repr(self, path=str(self.path))

    def __str__(self):
        return self.to_markdown()

    def virtual_files(self):
        return {self.path: self.to_markdown()}

    def to_markdown(self) -> str:
        header = self.get_header()
        content_str = self._to_markdown()
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

    def add_newlines(self, num: int):
        self.append("<br>" * num)

    def add_admonition(
        self,
        text: str,
        typ: admonition.AdmonitionTypeStr = "info",
        *,
        title: str | None = None,
        collapsible: bool = False,
    ) -> admonition.Admonition:
        item = admonition.Admonition(
            typ=typ,
            text=text,
            title=title,
            collapsible=collapsible,
        )
        self.append(item)
        return item

    def add_mkdocstrings(
        self,
        obj: types.ModuleType | str | os.PathLike | type,
        *,
        header: str = "",
        for_topmost: bool = False,
    ) -> docstrings.DocStrings:
        item = docstrings.DocStrings(obj=obj, header=header, for_topmost=for_topmost)
        self.append(item)
        return item

    def add_code(
        self,
        code: str | markdownnode.MarkdownNode,
        language: str = "",
        *,
        title: str = "",
        header: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
    ):
        item = codeblock.Code(
            code=code,
            language=language,
            title=title,
            header=header,
            linenums=linenums,
            highlight_lines=highlight_lines,
            parent=self,
        )
        self.append(item)
        return item


class ClassPage(MkPage):
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
        path: str | os.PathLike = "",
        **kwargs,
    ):
        path = pathlib.Path(f"{klass.__name__}.md")
        super().__init__(path=path, **kwargs)
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

    def _build(self):
        module_path = ".".join(self.parts).rstrip(".")
        path = f"{module_path}.{self.klass.__name__}"
        item = docstrings.DocStrings(path, header="DocStrings")
        self.append(item)
        if tbl := classtable.ClassTable(self.klass):
            self.append(tbl)
        diagram = mermaiddiagram.ClassDiagram(self.klass, header="Inheritance diagram")
        self.append(diagram)


class ModulePage(MkPage):
    """Page showing information about a module.

    Arguments:
        module: ModuleType or path to model to show info for.
        path: Some path for the file. Default is index.md
        docstrings: Whether to show docstrings for given module.
        show_class_table: ModuleType or path to model to show info for.
    """

    def __init__(
        self,
        module: tuple[str, ...] | str | types.ModuleType,
        *,
        path: str | os.PathLike = "index.md",
        docstrings: bool = False,
        show_class_table: bool = True,
        **kwargs,
    ):
        path = pathlib.Path(path)
        super().__init__(path=path, **kwargs)
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(self.parts)
        self.docstrings = docstrings
        self.show_class_table = show_class_table
        self._build()

    def __repr__(self):
        return utils.get_repr(self, module=self.module, path=str(self.path))

    @staticmethod
    def examples():
        yield dict(module="markdownizer")

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
            self.append(classtable.BaseClassTable(klasses))


if __name__ == "__main__":
    doc = MkPage()
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

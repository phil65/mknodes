from __future__ import annotations

import logging
import os
import pathlib
import types

from typing import Any, Literal

from markdownizer import (
    admonition,
    classhelpers,
    classtable,
    code as codeblock,
    diagram,
    docstrings,
    markdownnode,
    nav,
    utils,
)


logger = logging.getLogger(__name__)

HEADER = "---\n{options}\n---\n\n"


class MkPage(markdownnode.MarkdownContainer):
    """A node container representing a Markdown page.

    A page contains a list of other Markdown nodes, has a virtual Markdown file
    associated, and can have metadata (added as header)
    """

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
            self.header_options.setdefault("hide", []).append("navigation")
        if hide_path:
            self.header_options.setdefault("hide", []).append("path")

    def __repr__(self):
        return utils.get_repr(self, path=str(self.path))

    def __str__(self):
        return self.to_markdown()

    def virtual_files(self):
        return {self.path: self.to_markdown()}

    def to_markdown(self) -> str:
        header = self.formatted_header()
        content_str = self._to_markdown()
        return header + content_str if header else content_str

    def formatted_header(self) -> str:
        """Return the formatted header (containing metadata) for the page."""
        lines = []
        keys = self.header_options.keys()
        if not keys:
            return ""
        for option in keys:
            lines.append(f"{option}:")
            lines.extend(f"  - {area}" for area in self.header_options[option])
        return HEADER.format(options="\n".join(lines))

    def add_newlines(self, num: int):
        """Add line separators to the page."""
        self.append("<br>" * num)

    def add_header(self, text: str, level: int = 2):
        """Add line separators to the page."""
        prefix = "#" * level
        self.append(f"{prefix} {text}")

    def add_admonition(
        self,
        text: str,
        typ: admonition.AdmonitionTypeStr = "info",
        *,
        title: str | None = None,
        collapsible: bool = False,
    ) -> admonition.Admonition:
        """Add a Admonition info box to the page.

        Arguments:
            text: Text to display inside the box
            typ: the admonition type
            title: The title of the box
            collapsible: whether the box should be collapsible by the user.
        """
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
        allow_inspection: bool | None = None,
        show_bases: bool | None = None,
        show_source: bool | None = None,
        preload_modules: list[str] | None = None,
        heading_level: int | None = None,
        show_root_heading: bool | None = None,
        show_root_toc_entry: bool | None = None,
        show_root_full_path: bool | None = None,
        show_root_members_full_path: bool | None = None,
        show_object_full_path: bool | None = None,
        show_category_heading: bool | None = None,
        show_symbol_type_heading: bool | None = None,
        show_symbol_type_toc: bool | None = None,
        members: list[str] | None = None,
        members_order: Literal["alphabetical", "source"] | None = None,
        filters: list[str] | None = None,
        group_by_category: bool | None = None,
        show_submodules: bool | None = None,
        docstring_section_style: Literal["table", "list", "spacy"] | None = None,
        merge_init_into_class: bool | None = None,
        show_if_no_docstring: bool | None = None,
        annotations_path: Literal["brief", "source"] | None = None,
        line_length: int | None = None,
        show_signature: bool | None = None,
        show_signature_annotations: bool | None = None,
        signature_crossrefs: bool | None = None,
        separate_signature: bool | None = None,
    ) -> docstrings.DocStrings:
        """Add a DocStrings section to the page.

        Arguments:
            obj: What to show Docstrings for
            header: Section header
            for_topmost: whether to try to find the most topmost module path for given
                         object
            allow_inspection: Whether to allow inspecting modules when visiting
                              them is not possible
            show_bases: Show the base classes of a class.
            show_source: Show the source code of this object.
            preload_modules: List of modules to pre-load.
            heading_level: The initial heading level to use.
            show_root_heading: Show the heading of the object at the root of the
                               documentation tree (i.e. the object referenced by
                               the identifier after :::).
            show_root_toc_entry: If the root heading is not shown, at least
                                 add a ToC entry for it.
            show_root_full_path: Show the full Python path for the root
                                 object heading.
            show_root_members_full_path: Show the full Python path of the
                                         root members.
            show_object_full_path: Show the full Python path of every object.
            show_category_heading: When grouped by categories, show a heading
                                   for each category.
            show_symbol_type_heading: Show the symbol type in headings (e.g. mod,
                                      class, func and attr).
            show_symbol_type_toc: Show the symbol type in the Table of
                                  Contents (e.g. mod, class, func and attr).
            members: An explicit list of members to render.
            members_order: The members ordering to use.
            filters: A list of filters applied to filter objects based on their name.
                     A filter starting with ! will exclude matching objects instead of
                     including them. The members option takes precedence over filters
                     (filters will still be applied recursively to lower members in the
                     hierarchy).
            group_by_category: Group the object's children by categories:
                               attributes, classes, functions, and modules.
            show_submodules: When rendering a module, show its submodules recursively.
            docstring_section_style: The style used to render docstring sections.
            merge_init_into_class: Whether to merge the __init__ method into
                                   the class' signature and docstring.
            show_if_no_docstring: Show the object heading even if it has no
                                  docstring or children with docstrings.
            annotations_path: The verbosity for annotations path
            line_length: Maximum line length when formatting code/signatures.
            show_signature: Show methods and functions signatures.
            show_signature_annotations: Show the type annotations in methods
                                        and functions signatures.
            signature_crossrefs: Whether to render cross-references for type
                                 annotations in signatures.
            separate_signature: Whether to put the whole signature in a code
                                block below the heading. If Black is installed,
                                the signature is also formatted using it.
        """
        item = docstrings.DocStrings(
            obj=obj,
            header=header,
            for_topmost=for_topmost,
            allow_inspection=allow_inspection,
            show_bases=show_bases,
            show_source=show_source,
            preload_modules=preload_modules,
            heading_level=heading_level,
            show_root_heading=show_root_heading,
            show_root_toc_entry=show_root_toc_entry,
            show_root_full_path=show_root_full_path,
            show_root_members_full_path=show_root_members_full_path,
            show_object_full_path=show_object_full_path,
            show_category_heading=show_category_heading,
            show_symbol_type_heading=show_symbol_type_heading,
            show_symbol_type_toc=show_symbol_type_toc,
            members=members,
            members_order=members_order,
            filters=filters,
            group_by_category=group_by_category,
            show_submodules=show_submodules,
            docstring_section_style=docstring_section_style,
            merge_init_into_class=merge_init_into_class,
            show_if_no_docstring=show_if_no_docstring,
            annotations_path=annotations_path,
            line_length=line_length,
            show_signature=show_signature,
            show_signature_annotations=show_signature_annotations,
            signature_crossrefs=signature_crossrefs,
            separate_signature=separate_signature,
        )
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
        item = diagram.ClassDiagram(self.klass, header="Inheritance diagram")
        self.append(item)


if __name__ == "__main__":
    doc = MkPage()
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

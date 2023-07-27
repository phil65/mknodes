from __future__ import annotations

from collections.abc import Mapping
import logging
import os
import types

from typing import Any, Literal

import yaml

from mknodes import (
    mkadmonition,
    mkcode,
    mkcontainer,
    mkdocstrings,
    mklink,
    mknav,
    mknode,
    mktabcontainer,
    mktext,
)
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

HEADER = "---\n{options}---\n\n"


class MkPage(mkcontainer.MkContainer):
    """A node container representing a Markdown page.

    A page contains a list of other Markdown nodes, has a virtual Markdown file
    associated, and can have metadata (added as header)
    """

    def __init__(
        self,
        path: str | os.PathLike = "",
        *,
        hide_toc: bool | None = None,
        hide_nav: bool | None = None,
        hide_path: bool | None = None,
        search_boost: float | None = None,
        exclude_from_search: bool | None = None,
        icon: str | None = None,
        status: Literal["new", "deprecated"] | None = None,
        title: str | None = None,
        subtitle: str | None = None,
        description: str | None = None,
        parent: mknav.MkNav | None = None,
        **kwargs: Any,
    ):
        super().__init__(parent=parent, **kwargs)
        self.path = str(path)
        self.metadata: dict[str, Any] = {}
        if hide_toc is not None:
            self.metadata.setdefault("hide", []).append("toc")
        if hide_nav is not None:
            self.metadata.setdefault("hide", []).append("navigation")
        if hide_path is not None:
            self.metadata.setdefault("hide", []).append("path")
        if search_boost is not None:
            self.metadata.setdefault("search", {})["boost"] = search_boost
        if exclude_from_search is not None:
            self.metadata.setdefault("search", {})["exclude"] = exclude_from_search
        if icon is not None:
            self.metadata["icon"] = icon
        if status is not None:
            self.metadata["status"] = status
        if subtitle is not None:
            self.metadata["subtitle"] = subtitle
        if title is not None:
            self.metadata["title"] = title
        if description is not None:
            self.metadata["description"] = description

    def __repr__(self):
        return helpers.get_repr(self, path=str(self.path))

    def __str__(self):
        return self.to_markdown()

    def virtual_files(self) -> dict[str, str]:
        return {self.path: self.to_markdown()}

    def to_markdown(self) -> str:
        header = self.formatted_header()
        content_str = self._to_markdown()
        return header + content_str if header else content_str

    def formatted_header(self) -> str:
        """Return the formatted header (containing metadata) for the page."""
        if not self.metadata:
            return ""
        options = yaml.dump(self.metadata, Dumper=yaml.Dumper, indent=2)
        return HEADER.format(options=options)

    def add_newlines(self, num: int):
        """Add line separators to the page.

        Arguments:
            num: Amount of newlines to add.
        """
        self.append("<br>" * num)

    def add_link(
        self,
        url: str,
        title: str = "",
    ) -> mklink.MkLink:
        """Add a Link to the page.

        Arguments:
            url: URL to link to.
            title: Text to display for the link
        """
        item = mklink.MkLink(url, title)
        self.append(item)
        return item

    def add_header(self, text: str, level: int = 2) -> mktext.MkText:
        """Add line separators to the page.

        Arguments:
            text: header text
            level: header level
        """
        prefix = "#" * level
        node = mktext.MkText(f"{prefix} {text}")
        self.append(node)
        return node

    def add_admonition(
        self,
        text: str,
        typ: mkadmonition.AdmonitionTypeStr = "info",
        *,
        title: str | None = None,
        collapsible: bool = False,
    ) -> mkadmonition.MkAdmonition:
        """Add a Admonition info box to the page.

        Arguments:
            text: Text to display inside the box
            typ: the admonition type
            title: The title of the box
            collapsible: whether the box should be collapsible by the user.
        """
        item = mkadmonition.MkAdmonition(
            text=text,
            typ=typ,
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
    ) -> mkdocstrings.MkDocStrings:
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
        item = mkdocstrings.MkDocStrings(
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
        code: str | mknode.MkNode,
        language: str = "py",
        *,
        title: str = "",
        header: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
    ) -> mkcode.MkCode:
        """Add code block to the page.

        Arguments:
            code: Code
            language: language for syntax highlighting
            title: Optional title for the code block
            header: Optional header for the code block
            linenums: Optional start line number for the code block
            highlight_lines: Optional highlighting of a line range.
        """
        item = mkcode.MkCode(
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

    def add_tabs(
        self,
        data: Mapping[str, str | mknode.MkNode],
        *,
        style: Literal["tabbed", "tabblock"] = "tabbed",
        **kwargs: Any,
    ):
        """Add tabs to the page.

        Arguments:
            data: tab data
            style: Whether to use new-style (tabblock) or old-style (tabbed) tabs.
            kwargs: Keyword arguments passed to Tabs
        """
        if style == "tabbed":
            tabblock = mktabcontainer.MkTabbed(data, parent=self, **kwargs)
        else:
            tabblock = mktabcontainer.MkTabBlock(data, parent=self, **kwargs)
        self.append(tabblock)
        return tabblock


if __name__ == "__main__":
    doc = MkPage(hide_toc=True, search_boost=2)
    doc.add_link("test")
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

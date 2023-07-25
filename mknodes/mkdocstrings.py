from __future__ import annotations

import importlib
import logging
import os
import types

from typing import Any, Literal

from mknodes import mknode
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkDocStrings(mknode.MkNode):
    """Docstring section (powered by mkdocstrings)."""

    REQUIRED_PLUGINS = "mkdocstrings"
    OPTIONS_DEFAULT: dict[str, Any] = {}

    def __init__(
        self,
        obj: types.ModuleType
        | str
        | os.PathLike
        | type
        | types.FunctionType
        | types.MethodType,
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
        inherited_members: bool | None = None,
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
        **kwargs: Any,
    ):
        """Docstring section.

        Global options for DocStrings can be overridden by setting the keyword arguments
        to not-None.

        Arguments:
            obj: What to show DocStrings for.
            for_topmost: If True, try to find the "shortest" path to given object by
                         checking whether it can also be found in a parent module.
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
            inherited_members: Also show inherited members.
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
            kwargs: Keyword arguments passed to super.
        """
        super().__init__(**kwargs)
        self.obj = obj
        match obj:
            case types.ModuleType():
                self.obj_path = obj.__name__
            case type() | types.FunctionType() | types.MethodType():
                if for_topmost:
                    topmost_path = classhelpers.get_topmost_module_path(obj)
                    self.obj_path = f"{topmost_path}.{obj.__qualname__}"
                else:
                    self.obj_path = f"{obj.__module__}.{obj.__qualname__}"
            case str():
                self.obj_path = obj  # for setting a manual path
            case tuple() | list():
                self.obj_path = ".".join(obj)
            case os.PathLike():
                mod = importlib.import_module(os.fspath(obj))
                self.obj_path = mod.__name__
            case _:
                raise TypeError(obj)
        self.options = self.OPTIONS_DEFAULT.copy()
        self.options["allow_inspection"] = allow_inspection
        self.options["show_bases"] = show_bases
        self.options["show_source"] = show_source
        self.options["preload_modules"] = preload_modules
        self.options["heading_level"] = heading_level
        self.options["show_root_heading"] = show_root_heading
        self.options["show_root_toc_entry"] = show_root_toc_entry
        self.options["show_root_full_path"] = show_root_full_path
        self.options["show_root_members_full_path"] = show_root_members_full_path
        self.options["show_object_full_path"] = show_object_full_path
        self.options["show_category_heading"] = show_category_heading
        self.options["show_symbol_type_heading"] = show_symbol_type_heading
        self.options["show_symbol_type_toc"] = show_symbol_type_toc
        self.options["inherited_members"] = inherited_members
        self.options["members"] = members
        self.options["members_order"] = members_order
        self.options["filters"] = filters
        self.options["group_by_category"] = group_by_category
        self.options["show_submodules"] = show_submodules
        self.options["docstring_section_style"] = docstring_section_style
        self.options["merge_init_into_class"] = merge_init_into_class
        self.options["show_if_no_docstring"] = show_if_no_docstring
        self.options["annotations_path"] = annotations_path
        self.options["line_length"] = line_length
        self.options["show_signature"] = show_signature
        self.options["show_signature_annotations"] = show_signature_annotations
        self.options["signature_crossrefs"] = signature_crossrefs
        self.options["separate_signature"] = separate_signature
        self.options = {k: v for k, v in self.options.items() if v is not None}

    def __repr__(self):
        return helpers.get_repr(self, obj=self.obj)

    def _to_markdown(self) -> str:
        md = f"::: {self.obj_path}\n"
        if self.options:
            options = "\n".join(f"      {k}: {v!r}" for k, v in self.options.items())
            md = f"{md}    options:\n{options}\n"
        return md


if __name__ == "__main__":
    docstrings = MkDocStrings("a.b", show_submodules=True)
    print(docstrings)

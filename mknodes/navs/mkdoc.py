from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
import inspect
import pathlib
import types

from typing import Any

from mknodes.navs import mknav
from mknodes.pages import mkclasspage, mkmodulepage
from mknodes.utils import classhelpers, log, reprhelpers


logger = log.get_logger(__name__)


class MkDoc(mknav.MkNav):
    """Nav for showing a module documenation."""

    def __init__(
        self,
        module: types.ModuleType | Sequence[str] | str | None = None,
        *,
        filter_by___all__: bool = False,
        exclude_modules: list[str] | None = None,
        section_name: str | None = None,
        class_page: type[mkclasspage.MkClassPage] | None = None,
        module_page: type[mkmodulepage.MkModulePage] | None = None,
        flatten_nav: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: Module to document
            filter_by___all__: Whether to filter stuff according to "__all__"
            exclude_modules: List of modules to exclude
            section_name: Optional section name override
            class_page: Override for the default ClassPage
            module_page: Override for the default ModulePage
            flatten_nav: Whether classes should be put into top-level of the nav
            kwargs: Keyword arguments passed to parent
        """
        if module:
            self._module = classhelpers.to_module(module, return_none=False)
        else:
            self._module = None
        self.ClassPage = class_page or mkclasspage.MkClassPage
        self.ModulePage = module_page or mkmodulepage.MkModulePage
        self.flatten_nav = flatten_nav
        self.klasses: set[type] = set()
        self.submodules: set[types.ModuleType] = set()
        self.filter_by___all__ = filter_by___all__
        self._exclude = exclude_modules or []
        # self.root_path = pathlib.Path(f"./{self.module_name}")
        super().__init__(section=section_name or self.module_name, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            module=self.module_name,
            section=self.section or "<root>",
            filename=self.filename,
        )

    @property
    def module(self):
        return self.ctx.metadata.module if self._module is None else self._module

    @property
    def module_name(self):
        return self.module.__name__.split(".")[-1]

    def collect_classes(
        self,
        *,
        recursive: bool = False,
        predicate: Callable | None = None,
        submodule: types.ModuleType | str | tuple | list | None = None,
    ):
        for klass in self.iter_classes(
            recursive=recursive,
            predicate=predicate,
            submodule=submodule,
        ):
            self.klasses.add(klass)
        for klass in self.klasses:
            self.add_class_page(klass=klass, flatten=self.flatten_nav)
        for submod in self.submodules:
            self.add_doc(submod, class_page=self.ClassPage, flatten_nav=self.flatten_nav)
        self._create_index_page()

    def iter_classes(
        self,
        submodule: types.ModuleType | str | tuple | list | None = None,
        *,
        recursive: bool = False,
        predicate: Callable | None = None,
        _seen: set | None = None,
    ) -> Iterator[type]:
        """Iterate over all classes of the module.

        Arguments:
            submodule: filter based on a submodule
            recursive: whether to only iterate over members of current module
                       or whether it should also include classes from submodules.
            predicate: filter classes based on a predicate.
        """
        mod = classhelpers.to_module(submodule) if submodule else self.module
        if mod is None:
            return
        if recursive:
            seen = _seen or set()
            for _submod_name, submod in inspect.getmembers(mod, inspect.ismodule):
                if submod.__name__.startswith(self.module_name) and submod not in seen:
                    seen.add(submod)
                    yield from self.iter_classes(
                        submod,
                        recursive=True,
                        predicate=predicate,
                        _seen=seen,
                    )
        for klass_name, klass in inspect.getmembers(mod, inspect.isclass):
            if self.filter_by___all__ and (
                not hasattr(mod, "__all__") or klass_name not in mod.__all__
            ):
                continue
            if predicate and not predicate(klass):
                continue
            # if klass.__module__.startswith(self.module_name):
            if self.module_name in klass.__module__.split("."):
                yield klass

    def collect_modules(
        self,
        *,
        recursive: bool = False,
        predicate: Callable | None = None,
        submodule: types.ModuleType | str | tuple | list | None = None,
    ):
        for module in self.iter_modules(
            recursive=recursive,
            predicate=predicate,
            submodule=submodule,
        ):
            self.submodules.add(module)

    def iter_modules(
        self,
        *,
        submodule: types.ModuleType | str | tuple | list | None = None,
        recursive: bool = False,
        predicate: Callable | None = None,
        _seen: set | None = None,
    ) -> Iterator[types.ModuleType]:
        """Iterate over all submodules of the module.

        Arguments:
            submodule: filter based on a submodule
            recursive: whether to only iterate over members of current module
                       or whether it should also include modules from submodules.
            predicate: filter modules based on a predicate.
        """
        mod = classhelpers.to_module(submodule) if submodule else self.module
        seen = _seen or set()
        if mod is None:
            return
        for submod_name, submod in inspect.getmembers(mod, inspect.ismodule):
            not_in_all = hasattr(mod, "__all__") and submod_name not in mod.__all__
            filtered_by_all = self.filter_by___all__ and not_in_all
            not_filtered_by_pred = predicate(submod) if predicate else True
            # if self.module_name in mod.__name__.split(".")
            if not filtered_by_all and not_filtered_by_pred:
                yield submod
            if recursive and submod not in seen:
                seen.add(submod)
                yield from self.iter_modules(
                    submodule=submod,
                    recursive=True,
                    predicate=predicate,
                    _seen=seen,
                )

    def add_class_page(
        self,
        klass: type,
        *,
        find_topmost: bool = True,
        flatten: bool = False,
        **kwargs: Any,
    ) -> mkclasspage.MkClassPage:
        """Add a page showing information about a class.

        Arguments:
            klass: klass to build a page for
            find_topmost: Whether to use a module path from a parent package if available
            flatten: Put page into top level nav if nested.
            kwargs: keyword arguments passed to CLassPage
        """
        if find_topmost:
            parts = classhelpers.get_topmost_module_path(klass).split(".")
        else:
            parts = klass.__module__.split(".")
        # parts = klass.__module__.split(".")
        page = self.ClassPage(
            klass=klass,
            module_path=tuple(parts),
            path=pathlib.Path(f"{klass.__name__}.md"),
            parent=self,
            **kwargs,
        )
        section = (klass.__name__,) if flatten else (*parts[1:], klass.__name__)
        self.nav[section] = page
        return page

    def _create_index_page(
        self,
        title: str | None = None,
        **kwargs: Any,
    ) -> mkmodulepage.MkModulePage:
        """Add a page showing all submodules.

        Arguments:
            title: Override title for the section.
            kwargs: kwargs passed to MkModulePage.
        """
        page = self.ModulePage(
            hide_toc=True,
            module=self.module,
            klasses=self.klasses,
            path="index.md" if title is None else f"{title}.md",
            parent=self,
            **kwargs,
        )
        self.index_title = title or self.module_name
        self.index_page = page
        return page


if __name__ == "__main__":
    doc = MkDoc(module="mkdocs")
    page = doc.add_class_page(MkDoc)
    print(page)

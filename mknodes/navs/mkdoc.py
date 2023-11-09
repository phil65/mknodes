from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
import inspect
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
        recursive: bool = False,
        class_page: type[mkclasspage.MkClassPage] | str | None = None,
        module_page: type[mkmodulepage.MkModulePage] | str | None = None,
        flatten_nav: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: Module to document
            filter_by___all__: Whether to filter stuff according to "__all__"
            recursive: Whether to search modules recursively
            exclude_modules: List of modules to exclude
            section_name: Optional section title override
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
        self.recursive = recursive
        self.klasses: set[type] = set()
        self.submodules: set[types.ModuleType] = set()
        self.filter_by___all__ = filter_by___all__
        self._exclude = exclude_modules or []
        # self.root_path = pathlib.Path(f"./{self.module_name}")
        super().__init__(**kwargs)
        self.title = section_name or self.module_name
        self._collect_classes()

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            module=self.module_name,
            section=self.title or "<root>",
            filename=self.filename,
        )

    @property
    def module(self):
        return self.ctx.metadata.module if self._module is None else self._module

    @property
    def module_name(self) -> str:
        return self.module.__name__.split(".")[-1] if self.module else ""

    def _collect_classes(self):
        """Collect classes from given module."""
        for klass in self.iter_classes(recursive=self.recursive):
            self.klasses.add(klass)
        for klass in self.klasses:
            self.add_class_page(klass=klass, flatten=self.flatten_nav)
        for submod in self.submodules:
            self.add_doc(
                submod,
                class_page=self.ClassPage,
                filter_by___all__=self.filter_by___all__,
                module_page=self.ModulePage,
                flatten_nav=self.flatten_nav,
            )
        self._create_index_page()

    def iter_classes(
        self,
        submodule: types.ModuleType | str | tuple | list | None = None,
        *,
        recursive: bool = False,
        predicate: Callable[[type], bool] | None = None,
        _seen: set | None = None,
    ) -> Iterator[type]:
        """Iterate over all classes of the module.

        Arguments:
            submodule: filter based on a submodule
            recursive: whether to only iterate over members of current module
                       or whether it should also include classes from submodules.
            predicate: filter classes based on a predicate.
        """
        if isinstance(submodule, list):
            submodule = tuple(submodule)
        mod = classhelpers.to_module(submodule) if submodule else self.module
        if mod is None:
            return
        if recursive:
            seen = _seen or set()
            # TODO: pkgutil.iter_modules would also list "unknown" modules
            for submod in classhelpers.get_submodules(mod):
                if submod not in seen:
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
        if isinstance(self.ClassPage, str):
            page = mkclasspage.MkClassPage(
                klass=klass,
                template=self.ClassPage,
                module_path=tuple(parts),
                parent=self,
                **kwargs,
            )
        else:
            page = self.ClassPage(
                klass=klass,
                module_path=tuple(parts),
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
        path = "index.md" if title is None else f"{title}.md"
        if isinstance(self.ModulePage, str):
            page = mkmodulepage.MkModulePage(
                module=self.module,
                title=title or self.module_name,
                klasses=self.klasses,
                template_name=self.ModulePage,
                path=path,
                parent=self,
                **kwargs,
            )
        else:
            page = self.ModulePage(
                title=title or self.module_name,
                module=self.module,
                klasses=self.klasses,
                path=path,
                parent=self,
                **kwargs,
            )
        self.index_page = page
        return page


if __name__ == "__main__":
    doc = MkDoc(module="mkdocs")
    page = doc.add_class_page(MkDoc)
    print(page)

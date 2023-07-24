from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence

# import contextlib
# import importlib
import inspect
import logging
import pathlib
import types

from typing import Any

from mknodes import mknav
from mknodes.classnodes import mkclasspage
from mknodes.modulenodes import mkmodulepage
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkDoc(mknav.MkNav):
    """Nav for showing a module documenation.

    Arguments:
        module: Module to document
        filter_by___all__: Whether to filter stuff according to "__all__"
        exclude_modules: List of modules to exclude
        section_name: Optional section name override
        class_page: Override for the default ClassPage
                    (default: [MkClassPage](MkClassPage.md))
        flatten_nav: Whether classes should be put into top-level of the nav
    """

    def __init__(
        self,
        module: types.ModuleType | Sequence[str] | str,
        *,
        filter_by___all__: bool = False,
        exclude_modules: list[str] | None = None,
        section_name: str | None = None,
        class_page: type[mkclasspage.MkClassPage] | None = None,
        flatten_nav: bool = False,
        **kwargs,
    ):
        self.module = classhelpers.to_module(module, return_none=False)
        self.is_package = hasattr(self.module, "__path__")
        self.module_name = self.module.__name__.split(".")[-1]
        self.module_path = self.module.__name__
        self.file_path = self.module.__file__

        self.ClassPage = class_page or mkclasspage.MkClassPage
        self.flatten_nav = flatten_nav
        self.klasses: set[type] = set()
        self.submodules: set[types.ModuleType] = set()
        self.filter_by___all__ = filter_by___all__
        self._exclude = exclude_modules or []
        # self.root_path = pathlib.Path(f"./{self.module_name}")
        super().__init__(section=section_name or self.module_name, **kwargs)

    def __repr__(self):
        return helpers.get_repr(
            self,
            module=self.module_name,
            section=self.section or "<root>",
            filename=self.filename,
        )

    def to_markdown(self) -> str:
        self.add_module_overview()
        for klass in self.klasses:
            self.add_class_page(klass=klass, flatten=self.flatten_nav)
        for submod in self.submodules:
            self.add_doc(submod, class_page=self.ClassPage, flatten_nav=self.flatten_nav)
        return super().to_markdown()

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

    # def add_overview_page(self, predicate: Callable | None = None):
    #     page = mkpage.MkPage(
    #         hide_toc=True,
    #         path=pathlib.Path("index.md"),
    #         # parent=self,
    #     )
    #     page += mknodes.ModuleTable(self.module_name, predicate=predicate)
    #     return page

    def add_module_overview(
        self,
        title: str | None = None,
        **kwargs: Any,
    ) -> mkmodulepage.MkModulePage:
        """Add a page showing all submodules.

        Arguments:
            title: Override title for the section.
            kwargs: kwargs passed to MkModulePage.
        """
        # TODO: slugify?
        path = pathlib.Path("index.md" if title is None else f"{title}.md")
        # parts = path.parts[:-1]
        page = mkmodulepage.MkModulePage(
            hide_toc=True,
            module=self.module,
            klasses=self.klasses,
            path=path,
            parent=self,
            **kwargs,
        )
        self.nav[title or self.module_name] = page
        return page

    # def iter_files(self, glob: str = "*/*.py") -> Iterator[pathlib.Path]:
    #     """Iter through files based on glob.

    #     Arguments:
    #         glob: glob to use for filtering
    #     """
    #     for path in sorted(self.root_path.rglob(glob)):
    #         if (
    #             all(i not in path.parts for i in self._exclude)
    #             and not any(i.startswith("__") for i in path.parent.parts)
    #             and not path.is_dir()
    #         ):
    #             yield path.relative_to(self.root_path)

    # def iter_modules_for_glob(self, glob="*/*.py"):
    #     for path in self.iter_files(glob):
    #         module_path = path.with_suffix("")
    #         parts = tuple(module_path.parts)
    #         complete_module_path = f"{self.module_name}." + ".".join(parts)
    #         with contextlib.suppress(ImportError, AttributeError):
    #             yield importlib.import_module(complete_module_path)

    # def iter_classes_for_glob(
    #     self,
    #     glob: str = "*/*.py",
    #     *,
    #     recursive: bool = False,
    #     avoid_duplicates: bool = True,
    # ) -> Iterator[tuple[type, pathlib.Path]]:
    #     """Yields (class, path) tuples.

    #     Arguments:
    #         glob: glob to use for module file selection.
    #         recursive: Whether to search recursively.
    #         avoid_duplicates:

    #     """
    #     seen = set()
    #     for path in self.iter_files(glob):
    #         module_path = path.with_suffix("")
    #         parts = tuple(self.module_name, *module_path.parts)
    #         module = classhelpers.to_module(parts)
    #         if not module:
    #             return
    #         for klass in self.iter_classes(module, recursive=recursive):
    #             if (klass, path) not in seen or not avoid_duplicates:
    #                 seen.add((klass, path))
    #                 yield klass, path


if __name__ == "__main__":
    doc = MkDoc(module="mkdocs")
    page = doc.add_class_page(MkDoc)
    print(page)

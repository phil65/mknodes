from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.navs import mknav
from mknodes.pages import mkclasspage, mkmodulepage
from mknodes.utils import classhelpers, log, reprhelpers


if TYPE_CHECKING:
    from collections.abc import Sequence
    import types


logger = log.get_logger(__name__)


class MkDoc(mknav.MkNav):
    """Nav for showing a module documenation."""

    def __init__(
        self,
        module: types.ModuleType | Sequence[str] | str | None = None,
        *,
        filter_by___all__: bool = True,
        exclude_modules: list[str] | None = None,
        section_name: str | None = None,
        recursive: bool = False,
        class_template: str | None = None,
        module_template: str | None = None,
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
            class_template: Override for the default ClassPage template
            module_template: Override for the default ModulePage template
            flatten_nav: Whether classes should be put into top-level of the nav
            kwargs: Keyword arguments passed to parent
        """
        if module:
            self._module = classhelpers.to_module(module, return_none=False)
        else:
            self._module = None
        self.class_template = class_template
        self.module_template = module_template
        self.flatten_nav = flatten_nav
        self.recursive = recursive
        self.filter_by___all__ = filter_by___all__
        self._exclude = exclude_modules or []
        # self.root_path = pathlib.Path(f"./{self.module_name}")
        super().__init__(**kwargs)
        self.title = section_name or self.module_name

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            module=self.module_name,
            section=self.title or "<root>",
            filename=self.filename,
        )

    @property
    def children(self):
        if self.module is None:
            return []
        pages = []
        navs = []
        klasses = classhelpers.list_classes(
            module=self.module,
            filter_by___all__=self.filter_by___all__,
            module_filter=self.module_name,
        )
        for klass in klasses:
            p = self.add_class_page(klass=klass, flatten=self.flatten_nav)
            pages.append(p)
        for submod in classhelpers.get_submodules(
            self.module, filter_by___all__=self.filter_by___all__
        ):
            nav = self.add_doc(
                submod,
                class_template=self.class_template,
                filter_by___all__=self.filter_by___all__,
                module_template=self.module_template,
                flatten_nav=self.flatten_nav,
            )
            navs.append(nav)
        page = mkmodulepage.MkModulePage(
            module=self.module,
            title=self.module_name,
            is_index=True,
            klasses=klasses,
            template_path=self.module_template,
            parent=self,
        )
        self.index_page = page
        return pages + navs + [page]

    @children.setter
    def children(self, val):
        pass

    @property
    def module(self):
        return self.ctx.metadata.module if self._module is None else self._module

    @property
    def module_name(self) -> str:
        return self.module.__name__.split(".")[-1] if self.module else ""

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
        page = mkclasspage.MkClassPage(
            klass=klass,
            template_path=self.class_template,
            module_path=tuple(parts),
            parent=self,
            **kwargs,
        )
        section = (klass.__name__,) if flatten else (*parts[1:], klass.__name__)
        self.nav[section] = page
        return page


if __name__ == "__main__":
    doc = MkDoc(module="mkdocs")
    page = doc.add_class_page(MkDoc)
    print(page)

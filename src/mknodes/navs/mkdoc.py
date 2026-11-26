from typing import TYPE_CHECKING, Any

from mknodes.navs import apiscope, mknav
from mknodes.pages import mkclasspage, mkmodulepage
from mknodes.utils import classhelpers, log, reprhelpers


if TYPE_CHECKING:
    from collections.abc import Sequence
    import types
    from types import ModuleType


logger = log.get_logger(__name__)


class MkDoc(mknav.MkNav):
    """Nav for showing a module documentation.

    Every class gets exactly one page, below the module defining it (`pkg.sub.Klass` ->
    `<section>/sub/Klass/`), modules re-exporting it link to that page.
    With `recursive=True`, public submodules get their own (nested) MkDoc navs.
    """

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
    ) -> None:
        """Constructor.

        Args:
            module: Module to document
            filter_by___all__: Whether to filter stuff according to "__all__"
            recursive: Whether to add navs for submodules (recursively)
            exclude_modules: Modules to exclude (dotted path or module name)
            section_name: Optional section title override
            class_template: Override for the default ClassPage template
            module_template: Override for the default ModulePage template
            flatten_nav: Deprecated, has no effect. Class pages are always listed in the
                         nav of the module defining them.
            kwargs: Keyword arguments passed to parent
        """
        if module:
            self._module: ModuleType | None = classhelpers.to_module(module, return_none=False)
        else:
            self._module = None
        self.class_template = class_template
        self.module_template = module_template
        self.flatten_nav = flatten_nav
        self.recursive = recursive
        self.filter_by___all__ = filter_by___all__
        self._exclude = exclude_modules or []
        self._scope: apiscope.ApiScope | None = None
        self._doc_children: list[Any] | None = None
        # self.root_path = pathlib.Path(f"./{self.module_name}")
        super().__init__(**kwargs)
        self.title = section_name or self.module_name

    def __repr__(self) -> str:
        return reprhelpers.get_repr(
            self,
            module=self.module_name,
            section=self.title or "<root>",
            filename=self.filename,
        )

    @property
    def scope(self) -> apiscope.ApiScope | None:
        """The computed API scope (shared by all MkDocs of the tree)."""
        if self._scope is None and self.module is not None:
            self._scope = apiscope.ApiScope.build(
                self.module,
                recursive=self.recursive,
                filter_by___all__=self.filter_by___all__,
                exclude=self._exclude,
            )
        return self._scope

    def get_children(self):
        """Return computed children for module documentation.

        Class pages are put below the module defining the class, so the URL of class
        `Klass` of module `pkg.sub` is `<section>/sub/Klass/`, the module page is
        `<section>/sub/`. See `mknodes.navs.apiscope` for the rules.
        """
        if self.module is None:
            return []
        if self._doc_children is not None:
            return self._doc_children
        scope = self.scope
        assert scope is not None
        mod_name = self.module.__name__
        klasses = scope.classes_for(mod_name)
        pages = [
            self.add_class_page(klass=klass, path=scope.page_names[klass]) for klass in klasses
        ]
        navs = []
        for submod_name in scope.children.get(mod_name, []):
            nav = MkDoc(
                scope.modules[submod_name],
                class_template=self.class_template,
                filter_by___all__=self.filter_by___all__,
                recursive=True,
                module_template=self.module_template,
                flatten_nav=self.flatten_nav,
                exclude_modules=self._exclude,
                parent=self,
            )
            nav._scope = scope
            self.nav.register(nav)
            navs.append(nav)
        page = mkmodulepage.MkModulePage(
            module=self.module,
            title=self.module_name,
            is_index=True,
            klasses=klasses,
            reexported=scope.reexports_for(mod_name),
            template_path=self.module_template,
            parent=self,
        )
        self.index_page = page
        self.ctx.links.register_object_page(mod_name, page)
        self._doc_children = [*pages, *navs, page]
        return self._doc_children

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
        path: str | None = None,
        **kwargs: Any,
    ) -> mkclasspage.MkClassPage:
        """Add a page showing information about a class to this nav.

        Links to the class (class tables, base classes, ...) point to this page.

        Args:
            klass: klass to build a page for
            find_topmost: Deprecated, has no effect. The mkdocstrings directive always
                          uses the path of the defining module.
            flatten: Deprecated, has no effect. Class pages always get listed in the nav
                     of the module they belong to.
            path: Page name (file stem). Defaults to the class name.
            kwargs: keyword arguments passed to MkClassPage
        """
        page = mkclasspage.MkClassPage(
            klass=klass,
            template_path=self.class_template,
            path=path or klass.__name__,
            parent=self,
            **kwargs,
        )
        self.nav[page.path.removesuffix(".md"),] = page
        self.ctx.links.register_object_page(apiscope.class_path(klass), page)
        return page


if __name__ == "__main__":
    doc = MkDoc(module="mkdocs")
    page = doc.add_class_page(MkDoc)
    print(page)

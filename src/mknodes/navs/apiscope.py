"""Scope of an API documentation: which modules get a page, and where each class lives.

Rules (used by [MkDoc][mknodes.MkDoc]):

- Every documented class gets exactly one page, below the module that defines it
  (`cls.__module__`).
- If the defining module does not get a page (it is private like `pkg._impl`, excluded,
  or outside of the documented tree), the class lives in the public module that
  exports it and is closest to the defining module. Classes of private modules that are
  not exported by any public module live in the nearest public parent module.
- Modules that only re-export a class link to its page instead of duplicating it.
- Private modules (`_foo`) and `__main__` never get pages of their own.

URL scheme: module `pkg.sub` -> `<section>/sub/` (`index.md`), its class `Klass` ->
`<section>/sub/Klass/`. Class page names keep the class name (case included). A class
whose name clashes (case-insensitively) with a documented submodule of its module or with the
reserved names `index` / `README` / `SUMMARY` gets the suffix `-class`, which can't clash
with a module name since module names are identifiers.
"""

import dataclasses
import importlib
import inspect
import pkgutil
from typing import TYPE_CHECKING

from mknodes.utils import classhelpers, log


if TYPE_CHECKING:
    from collections.abc import Iterable, Iterator
    import types


logger = log.get_logger(__name__)

# Page names (lowercase) that are used by navs / index pages.
RESERVED_PAGE_NAMES = frozenset({"index", "readme", "summary"})


def class_path(klass: type) -> str:
    """Return the dotted path of the module defining given class plus its qualname."""
    return f"{klass.__module__}.{klass.__qualname__}"


def _common_prefix_len(a: str, b: str) -> int:
    n = 0
    for x, y in zip(a.split("."), b.split("."), strict=False):
        if x != y:
            break
        n += 1
    return n


def _submodule_names(module: types.ModuleType) -> list[str]:
    """Return names of all direct submodules of given module (without importing them)."""
    if not hasattr(module, "__path__"):
        return []
    return [name for _finder, name, _ispkg in pkgutil.iter_modules(module.__path__)]


def unique_page_name(name: str, taken: set[str]) -> str:
    """Return a page name for a class which does not clash with given (lowercase) names.

    Args:
        name: The class name
        taken: Lowercase names already in use in the same folder. Gets updated.
    """
    candidate = name
    i = 1
    while candidate.lower() in taken:
        candidate = f"{name}-class" if i == 1 else f"{name}-class-{i}"
        i += 1
    taken.add(candidate.lower())
    return candidate


@dataclasses.dataclass
class ApiScope:
    """Computed layout of an API documentation tree."""

    root: str
    """Dotted path of the documented root module."""
    filter_by___all__: bool = False
    """Only include classes / submodules listed in `__all__`."""
    modules: dict[str, types.ModuleType] = dataclasses.field(default_factory=dict)
    """Modules which get a page (root first, depth-first order)."""
    children: dict[str, list[str]] = dataclasses.field(default_factory=dict)
    """Module path -> paths of the submodules which get a page."""
    exports: dict[str, list[type]] = dataclasses.field(default_factory=dict)
    """Module path -> public classes reachable as members of the module."""
    homes: dict[type, str] = dataclasses.field(default_factory=dict)
    """Class -> path of the module whose page lists it."""
    page_names: dict[type, str] = dataclasses.field(default_factory=dict)
    """Class -> page name (file stem) of its class page."""

    @classmethod
    def build(
        cls,
        module: types.ModuleType,
        *,
        recursive: bool = False,
        filter_by___all__: bool = False,
        exclude: Iterable[str] = (),
    ) -> ApiScope:
        """Compute the scope for given root module.

        Args:
            module: Root module of the documentation
            recursive: Whether to include submodules (recursively)
            filter_by___all__: Only include classes / submodules listed in `__all__`
            exclude: Modules (dotted path or name) to leave out
        """
        scope = cls(root=module.__name__, filter_by___all__=filter_by___all__)
        excluded = set(exclude)
        top_level = module.__name__.split(".")[0]
        private: list[types.ModuleType] = []
        for mod in scope._walk(module, recursive=recursive, excluded=excluded):
            if scope.is_private(mod.__name__):
                private.append(mod)
                continue
            scope.modules[mod.__name__] = mod
            scope.children[mod.__name__] = []
            if mod.__name__ != scope.root:
                parent = mod.__name__.rpartition(".")[0]
                scope.children.setdefault(parent, []).append(mod.__name__)
        for name, mod in scope.modules.items():
            scope.exports[name] = scope._public_classes(mod, top_level)
        candidates: dict[type, None] = {}
        for klasses in scope.exports.values():
            candidates.update(dict.fromkeys(klasses))
        for mod in private:
            defined = [
                k for k in scope._public_classes(mod, top_level) if k.__module__ == mod.__name__
            ]
            candidates.update(dict.fromkeys(defined))
        for klass in candidates:
            scope.homes[klass] = scope._find_home(klass)
        for mod_name in scope.modules:
            # the folder of a module only contains its index page, its class pages
            # and the folders of its documented submodules
            subfolders = {c.rpartition(".")[2].lower() for c in scope.children[mod_name]}
            taken = set(RESERVED_PAGE_NAMES) | subfolders
            for klass in scope.classes_for(mod_name):
                scope.page_names[klass] = unique_page_name(klass.__name__, taken)
        return scope

    def is_private(self, module_name: str) -> bool:
        """Return whether given module is private relative to the root module."""
        if module_name == self.root:
            return False
        rel = module_name.removeprefix(f"{self.root}.")
        return any(part.startswith("_") for part in rel.split("."))

    def _walk(
        self,
        module: types.ModuleType,
        *,
        recursive: bool,
        excluded: set[str],
    ) -> Iterator[types.ModuleType]:
        yield module
        if not recursive:
            return
        names = _submodule_names(module)
        if self.filter_by___all__:
            # filter before importing, so unlisted (e.g. optional) submodules are never imported
            export = getattr(module, "__all__", [])
            names = [name for name in names if name in export]
        for name in names:
            path = f"{module.__name__}.{name}"
            if name == "__main__" or name in excluded or path in excluded:
                continue
            try:
                submod = importlib.import_module(path)
            except Exception:  # noqa: BLE001
                logger.warning("Could not import %s, skipping it in the API docs", path)
                continue
            yield from self._walk(submod, recursive=True, excluded=excluded)

    def _public_classes(self, module: types.ModuleType, top_level: str) -> list[type]:
        """Return public classes of the package reachable as members of given module."""
        names = getattr(module, "__all__", None)
        allowed = set(names or ()) if self.filter_by___all__ else None
        result: list[type] = []
        for name, klass in classhelpers.get_members(module, inspect.isclass):
            if allowed is not None:
                if name not in allowed:
                    continue
            elif name.startswith("_"):
                continue
            mod_name = getattr(klass, "__module__", None) or ""
            if mod_name != top_level and not mod_name.startswith(f"{top_level}."):
                continue
            if klass not in result:
                result.append(klass)
        return result

    def _find_home(self, klass: type) -> str:
        defining = klass.__module__
        if defining in self.modules:
            return defining
        exporters = [name for name, klasses in self.exports.items() if klass in klasses]
        if exporters:
            # closest to the defining module, shallowest on ties
            return max(exporters, key=lambda m: (_common_prefix_len(m, defining), -m.count(".")))
        parts = defining.split(".")
        while parts:
            if (name := ".".join(parts)) in self.modules:
                return name
            parts.pop()
        return self.root

    def classes_for(self, module_name: str) -> list[type]:
        """Return the classes whose page belongs to given module, sorted by name."""
        klasses = [k for k, home in self.homes.items() if home == module_name]
        return sorted(klasses, key=lambda k: k.__name__)

    def reexports_for(self, module_name: str) -> list[type]:
        """Return the classes exported by given module whose page lives elsewhere.

        Only packages and modules with an `__all__` count as re-exporting, so plain
        modules which import a class for internal use don't list it.
        """
        module = self.modules[module_name]
        if not hasattr(module, "__all__") and not hasattr(module, "__path__"):
            return []
        klasses = [k for k in self.exports.get(module_name, []) if self.homes[k] != module_name]
        return sorted(klasses, key=lambda k: k.__name__)

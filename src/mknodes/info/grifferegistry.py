from abc import ABCMeta
from collections.abc import MutableMapping
import threading
import types
from typing import TYPE_CHECKING

import griffe

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Iterator


logger = log.get_logger(__name__)


def get_module(module: str | types.ModuleType) -> griffe.Module | griffe.Alias:
    """Return info for given module from registry.

    Args:
        module: Name of the module
    """
    return registry.get_module(module)


def get_class(klass: str | type) -> griffe.Class | griffe.Alias:
    """Return info for given klass from registry.

    Args:
        klass: Name of the klass
    """
    return registry.get_class(klass)


# Modules that only re-export members of another module, mapped to the defining module.
_MODULE_ALIASES = {"collections.abc": "_collections_abc"}


class GriffeRegistry(MutableMapping[str, griffe.Module], metaclass=ABCMeta):
    """Registry for Griffe Modules.

    Used for accessing / caching all loaded Griffe objects.
    The registry will always only create the Griffe module for the top-level module
    and then use griffe_module[submodule] or griffe_module[klass] to get the
    griffe instances. That should enable the best cache behaviour.

    Examples:
        ``` py
        reg = GriffeRegistry()
        griffe_module = reg.get_module("my_module")
        another_module = reg.get_module("my_module.submodule")
        ```
    """

    def __init__(self, expand_wildcards: bool = True) -> None:
        """Instanciate the registry.

        Args:
            expand_wildcards: Whether to expand wildcard imports for the Modules
        """
        self.expand_wildcards = expand_wildcards
        self._modules: dict[str, griffe.Module] = {}
        # Route functions / pages may load packages from several threads at once.
        self._lock = threading.RLock()

    def __getitem__(self, value: str) -> griffe.Module:
        return self._modules.__getitem__(value)

    def __setitem__(self, index: str, value: griffe.Module) -> None:
        self._modules[index] = value

    def __delitem__(self, index: str) -> None:
        del self._modules[index]

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __iter__(self) -> Iterator[str]:
        return iter(self._modules.keys())

    def __len__(self) -> int:
        return len(self._modules)

    def get_module(
        self,
        module: str | types.ModuleType,
        docstring_style: griffe.Parser = griffe.Parser.auto,
    ) -> griffe.Module | griffe.Alias:
        """Get griffe Module for given module.

        Args:
            module: Module to get griffe object for
            docstring_style: Docstring style
        """
        if isinstance(module, types.ModuleType):
            module = module.__name__
        if "." in module:
            module_name, sub_mod_path = module.split(".", 1)
        else:
            module_name, sub_mod_path = module, ""
        if module_name not in self._modules:
            with self._lock:
                if module_name not in self._modules:  # another thread may have loaded it
                    self._modules[module_name] = self._load(module_name, docstring_style)
        griffe_mod = self._modules[module_name]
        return griffe_mod[sub_mod_path] if sub_mod_path else griffe_mod

    def _load(self, module_name: str, docstring_style: griffe.Parser) -> griffe.Module:
        parser = griffe.Parser(docstring_style)
        loader = griffe.GriffeLoader(docstring_parser=parser)
        griffe_mod = loader.load(module_name)
        assert isinstance(griffe_mod, griffe.Object)
        if self.expand_wildcards:
            loader.expand_wildcards(griffe_mod, external=True)  # pyright: ignore[reportUnknownMemberType]
        assert isinstance(griffe_mod, griffe.Module)
        return griffe_mod

    def get_class(
        self,
        klass: str | type,
        docstring_style: griffe.Parser = griffe.Parser.auto,
    ) -> griffe.Class | griffe.Alias:
        """Get griffe Class for given class.

        Args:
            klass: Class to get Griffe object for
            docstring_style: Docstring style
        """
        if isinstance(klass, type):
            mod_name = klass.__module__
            if "." in mod_name:
                mod_name, sub_mod_path = mod_name.split(".", 1)
            else:
                mod_name, sub_mod_path = mod_name, ""
            qual_name = klass.__qualname__
            kls_name = f"{sub_mod_path}.{qual_name}" if sub_mod_path else qual_name
        else:
            parts = klass.split(".", 1)
            mod_name, kls_name = parts if len(parts) > 1 else ("builtins", parts[0])
        kls_name = kls_name.split("[")[0]
        module = self.get_module(mod_name, docstring_style=docstring_style)
        try:
            return module[kls_name]
        except KeyError:
            # Some stdlib modules only re-export their members (e.g. `collections.abc`
            # is `from _collections_abc import *`), which griffe can't resolve statically.
            full_mod, _, name = f"{mod_name}.{kls_name}".rpartition(".")
            if (alias := _MODULE_ALIASES.get(full_mod)) is None:
                raise
            return self.get_module(alias, docstring_style=docstring_style)[name]


registry = GriffeRegistry()


if __name__ == "__main__":
    reg = GriffeRegistry()
    reg.get_module("mknodes.basenodes")
    info = reg.get_class("mknodes.MkAdmonition")

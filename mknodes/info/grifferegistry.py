from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping
import types

import griffe

from mknodes.utils import log


logger = log.get_logger(__name__)


def get_module(module: str | types.ModuleType) -> griffe.Module | griffe.Alias:
    """Return info for given module from registry.

    Arguments:
        module: Name of the module
    """
    return registry.get_module(module)


def get_class(klass: str | type) -> griffe.Class | griffe.Alias:
    """Return info for given klass from registry.

    Arguments:
        klass: Name of the klass
    """
    return registry.get_class(klass)


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

    def __init__(self, expand_wildcards: bool = True):
        """Instanciate the registry.

        Arguments:
            expand_wildcards: Whether to expand wildcard imports for the Modules
        """
        self.expand_wildcards = expand_wildcards
        self._modules: dict[str, griffe.Module] = {}

    def __getitem__(self, value: str):
        return self._modules.__getitem__(value)

    def __setitem__(self, index: str, value: griffe.Module):
        self._modules[index] = value

    def __delitem__(self, index: str):
        del self._modules[index]

    def __repr__(self):
        return f"{type(self).__name__}()"

    def __iter__(self):
        return iter(self._modules.keys())

    def __len__(self):
        return len(self._modules)

    def get_module(
        self,
        module: str | types.ModuleType,
        docstring_style: str = "google",
    ) -> griffe.Module | griffe.Alias:
        """Get griffe Module for given module.

        Arguments:
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
            parser = griffe.Parser(docstring_style)
            loader = griffe.GriffeLoader(docstring_parser=parser)
            griffe_mod = loader.load(module_name)
            assert isinstance(griffe_mod, griffe.Object)
            if self.expand_wildcards:
                loader.expand_wildcards(griffe_mod, external=True)
            self._modules[module_name] = griffe_mod
        griffe_mod = self._modules[module_name]
        return griffe_mod[sub_mod_path] if sub_mod_path else griffe_mod

    def get_class(
        self,
        klass: str | type,
        docstring_style: str = "google",
    ) -> griffe.Class | griffe.Alias:
        """Get griffe Class for given class.

        Arguments:
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
        module = self.get_module(mod_name, docstring_style=docstring_style)
        return module[kls_name]


registry = GriffeRegistry()


if __name__ == "__main__":
    reg = GriffeRegistry()
    reg.get_module("mknodes.basenodes")
    info = reg.get_class("mknodes.MkAdmonition")

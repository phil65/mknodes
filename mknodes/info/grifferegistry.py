from __future__ import annotations

from abc import ABCMeta
from collections.abc import MutableMapping
import types

import griffe

from griffe.enumerations import Parser
from griffe.loader import GriffeLoader

from mknodes.utils import log


logger = log.get_logger(__name__)


def get_module(module: str | types.ModuleType) -> griffe.Module:
    """Return info for given module from registry.

    Arguments:
        module: Name of the module
    """
    return registry.get_module(module)


class GriffeRegistry(MutableMapping, metaclass=ABCMeta):
    """Registry for PackageInfos.

    Used for caching all loaded Package information.
    """

    def __init__(self):
        self._modules: dict[str, griffe.Module] = {}

    def __getitem__(self, value):
        return self._modules.__getitem__(value)

    def __setitem__(self, index, value):
        self._modules[index] = value

    def __delitem__(self, index):
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
    ) -> griffe.Module:
        """Get package information for given module.

        Arguments:
            module: Name of the module
            docstring_style: Docstring style
        """
        if isinstance(module, types.ModuleType):
            module = module.__name__
        if module not in self._modules:
            parser = Parser(docstring_style)
            loader = GriffeLoader(docstring_parser=parser)
            self._modules[module] = loader.load_module(module)
        return self._modules[module]


registry = GriffeRegistry()


if __name__ == "__main__":
    reg = GriffeRegistry()
    info = reg.get_module("mknodes")
    print(info.members)

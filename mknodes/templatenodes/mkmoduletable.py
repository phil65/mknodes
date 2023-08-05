from __future__ import annotations

from collections.abc import Sequence
import inspect
import logging
import types

from mknodes.basenodes import mktable
from mknodes.utils import classhelpers, helpers, layouts


logger = logging.getLogger(__name__)


class MkModuleTable(mktable.MkTable):
    """Class representing a formatted table containing information a module."""

    ICON = "material/view-module-outline"

    def __init__(
        self,
        modules: Sequence[types.ModuleType | str | tuple[str, ...]],
        **kwargs,
    ):
        self.modules = [classhelpers.to_module(i, return_none=False) for i in modules]
        layout = layouts.ModuleLayout()
        dicts = [layout.get_row_for(mod) for mod in self.modules]
        super().__init__(dicts, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, modules=self.modules)

    @staticmethod
    def create_example_page(page):
        import mkdocstrings

        import mknodes

        modules = [mod for _, mod in inspect.getmembers(mkdocstrings, inspect.ismodule)]
        node = MkModuleTable(modules=modules)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    table = MkModuleTable(modules=[mktable, helpers, classhelpers])
    print(table)

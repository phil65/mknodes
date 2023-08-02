from __future__ import annotations

from collections.abc import Sequence
import inspect
import logging
import types

from mknodes.basenodes import mktable
from mknodes.utils import classhelpers, helpers


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
        dicts = [self.get_row_for_module(mod) for mod in self.modules]
        super().__init__(dicts, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, modules=self.modules)

    def get_row_for_module(self, module: types.ModuleType) -> dict[str, str]:
        return dict(
            Name=module.__name__,
            # helpers.link_for_class(submod, size=4, bold=True),
            DocStrings=helpers.get_doc(
                module,
                fallback="*No docstrings defined.*",
                only_summary=True,
            ),
            Members=(
                helpers.to_html_list(module.__all__, make_link=True)
                if hasattr(module, "__all__")
                else ""
            ),
        )

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

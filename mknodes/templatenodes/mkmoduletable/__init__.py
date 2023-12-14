from __future__ import annotations


from mknodes.info import grifferegistry
from mknodes.templatenodes import mktemplatetable
from mknodes.utils import classhelpers, helpers, log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import types
    from collections.abc import Sequence


logger = log.get_logger(__name__)


class MkModuleTable(mktemplatetable.MkTemplateTable):
    """Node for a table containing formatted information about a module."""

    ICON = "material/view-module-outline"

    def __init__(
        self,
        modules: Sequence[types.ModuleType | str],
        **kwargs,
    ):
        self.modules = [classhelpers.to_module(i, return_none=False) for i in modules]
        super().__init__(**kwargs)

    def iter_items(self):
        yield from [
            dict(module=module, griffe_module=grifferegistry.get_module(module))
            for module in self.modules
        ]


if __name__ == "__main__":
    table = MkModuleTable(modules=[mktemplatetable, helpers, classhelpers])
    print(table)

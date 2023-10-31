from __future__ import annotations

import types

from typing import Any

from mknodes import treelib
from mknodes.templatenodes import mktreeview
from mknodes.utils import classhelpers, log


logger = log.get_logger(__name__)


class MkModuleOverview(mktreeview.MkTreeView):
    """Node to display a module and its submodules as a tree.

    Submodule names and the first docstring line are shown for each
    submodule.
    """

    ICON = "material/file-tree-outline"
    STATUS = "new"

    def __init__(
        self,
        module: types.ModuleType | str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: Module to display.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("", **kwargs)
        self._module = module

    @property
    def tree(self):
        match self._module:
            case types.ModuleType():
                return self._module
            case str():
                return classhelpers.to_module(self._module)
            case _:
                return self.ctx.metadata.module

    @tree.setter
    def tree(self, value):
        self._module = value

    @property
    def text(self):
        if not self.tree:
            return ""
        node = treelib.ModuleNode.from_module(
            self.tree,
            predicate=self.predicate,
            exclude=self.exclude_folders,
        )
        max_depth = self.maximum_depth or 0
        return node.get_tree_repr(style=self.style, max_depth=max_depth)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkModuleOverview(maximum_depth=2)
        page += mk.MkReprRawRendered(node, header="### From project")

        import git

        node = MkModuleOverview(git, maximum_depth=2)
        page += mk.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    import mknodes as mk

    node = MkModuleOverview(mk, header="test", style="ascii")
    print(node.to_markdown())

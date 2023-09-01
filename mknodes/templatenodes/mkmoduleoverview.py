from __future__ import annotations

import logging
import types

from typing import Any

from mknodes import treelib
from mknodes.templatenodes import mktreeview
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkModuleOverview(mktreeview.MkTreeView):
    """Node to display a module and its submodules as a tree.

    Submodule names and the first docstring line are shown for each
    submodule.
    """

    ICON = "material/file-tree-outline"
    STATUS = "new"

    def __init__(
        self,
        module: types.ModuleType | None = None,
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
            case None if self.associated_project:
                return self.associated_project.folderinfo.module
            case types.ModuleType():
                return self._module
            case _:
                return None

    @tree.setter
    def tree(self, value):
        self._module = value

    @property
    def text(self):
        node = treelib.ModuleNode.from_module(
            self.tree,
            predicate=self.predicate,
            exclude=self.exclude_folders,
        )
        return node.get_tree_repr(
            style=self.style,
            max_depth=self.maximum_depth or 0,
        )

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            module=self.tree,
            style=self._style,
            maximum_depth=self.maximum_depth,
            _filter_empty=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkModuleOverview(maximum_depth=2)
        page += mknodes.MkReprRawRendered(node, header="### From project")
        import mkdocs

        node = MkModuleOverview(mkdocs, maximum_depth=2)
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    import mknodes

    node = MkModuleOverview(mknodes, header="test", style="ascii")
    print(node.to_markdown())

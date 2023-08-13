from __future__ import annotations

from collections.abc import Callable
import inspect
import logging
import types

from mknodes.treelib import node
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class ModuleNode(node.Node):
    def __init__(self, module: types.ModuleType, **kwargs):
        self.module = module
        self.summary = helpers.get_doc(self.module, only_summary=True)
        super().__init__(**kwargs)

    def __repr__(self):
        module_name = self.module.__name__.split(".")[-1]
        if self.summary:
            module_name += f": {self.summary}"
        return module_name

    @classmethod
    def from_module(
        cls,
        module: types.ModuleType,
        *,
        predicate: Callable | None = None,
        exclude: list[str] | None = None,
        sort: bool = True,
        max_items: int | None = None,
        maximum_depth: int | None = None,
        parent: ModuleNode | None = None,
    ):
        node = cls(module, parent=parent)
        children = [
            mod
            for _name, mod in inspect.getmembers(module, inspect.ismodule)
            if mod.__name__.startswith(module.__name__)
        ]
        if sort:
            children = sorted(children, key=lambda s: s.__name__.lower())
        for submod in children:
            if predicate and not predicate(submod):
                continue
            if exclude and submod.__name__ in exclude:
                continue
            if not children:
                child = cls(submod, parent=node)
            else:
                if maximum_depth is not None and maximum_depth < node.depth + 1:
                    continue
                child = ModuleNode.from_module(
                    submod,
                    parent=node,
                    predicate=predicate,
                    max_items=max_items,
                    maximum_depth=maximum_depth,
                    exclude=exclude,
                )
            if max_items is not None:
                if max_items > 0:
                    max_items -= 1
                else:
                    break

            node.append_child(child)
        return node


if __name__ == "__main__":
    import mknodes

    folder = ModuleNode.from_module(mknodes)
    logger.warning(folder.get_tree_repr())
    # node = ModuleNode(mknodes)
    # print(node.children)
    # logger.warning(node.get_tree_repr())

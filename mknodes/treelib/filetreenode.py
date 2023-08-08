from __future__ import annotations

from collections.abc import Callable
import logging
import os
import pathlib

from typing import TypeVar

from mknodes.treelib import node


logger = logging.getLogger(__name__)


class FileTreeNode(node.Node):
    def __init__(self, path, **kwargs):
        self.path = pathlib.Path(path)
        self.sep = "/"
        super().__init__(**kwargs)

    @property
    def path_name(self):
        return str(self.path)

    def __repr__(self):
        return f"{self.path.name}/" if self.path.is_dir() else self.path.name

    @classmethod
    def from_folder(
        cls,
        folder: str | os.PathLike,
        predicate: Callable | None = None,
        parent: FileTreeNode | None = None,
    ):
        folder = pathlib.Path(folder)
        if predicate:
            pred_fn = predicate
        else:

            def pred_fn(x):
                return True

        node = cls(folder, parent=parent)
        children = sorted(
            [path for path in folder.iterdir() if pred_fn(path)],
            key=lambda s: str(s).lower(),
        )
        for path in children:
            child = (
                cls(path, parent=node)
                if path.is_file()
                else FileTreeNode.from_folder(path, parent=node)
            )
            node.append_child(child)
        return node


T = TypeVar("T", bound=FileTreeNode)


if __name__ == "__main__":
    from mknodes.treelib import get_tree_repr

    folder = FileTreeNode.from_folder(".")
    print(get_tree_repr(folder))

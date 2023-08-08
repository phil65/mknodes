from __future__ import annotations

import logging
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
    def from_folder(cls, folder):
        folder = pathlib.Path(folder)
        node = cls(folder)
        for path in folder.iterdir():
            child = cls(path) if path.is_file() else FileTreeNode.from_folder(path)
            node.append_child(child)
        return node


T = TypeVar("T", bound=FileTreeNode)


if __name__ == "__main__":
    folder = FileTreeNode.from_folder(".")

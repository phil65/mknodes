from __future__ import annotations

from collections.abc import Callable
import logging
import os
import pathlib

from mknodes.treelib import node


logger = logging.getLogger(__name__)


class FileTreeNode(node.Node):
    def __init__(self, path, **kwargs):
        self.path = pathlib.Path(path)
        self.name = self.path.name
        self.type = "folder" if self.path.is_dir() else "file"
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.name}/" if self.type == "folder" else self.name

    @classmethod
    def from_folder(
        cls,
        folder: str | os.PathLike,
        *,
        predicate: Callable | None = None,
        exclude_folders: list[str] | None = None,
        sort: bool = True,
        max_items: int | None = None,
        maximum_depth: int | None = None,
        parent: FileTreeNode | None = None,
    ):
        folder = pathlib.Path(folder)
        node = cls(folder, parent=parent)
        children = list(folder.iterdir())
        if sort:
            children = sorted(children, key=lambda s: str(s).lower())
        for path in children:
            if predicate and not predicate(path):
                continue
            if exclude_folders and path.name in exclude_folders and path.is_dir():
                continue
            if path.is_file():
                child = cls(path, parent=node)
            else:
                if maximum_depth is not None and maximum_depth < node.depth + 1:
                    continue
                child = FileTreeNode.from_folder(
                    path,
                    parent=node,
                    predicate=predicate,
                    max_items=max_items,
                    maximum_depth=maximum_depth,
                    exclude_folders=exclude_folders,
                )
            if max_items is not None:
                if max_items > 0:
                    max_items -= 1
                else:
                    break

            node.append_child(child)
        return node

    def get_folder_count(self) -> int:
        return sum(i.type == "folder" for i in self.descendants)

    def get_file_count(self) -> int:
        return sum(i.type == "file" for i in self.descendants)


if __name__ == "__main__":
    folder = FileTreeNode.from_folder(
        ".",
        exclude_folders=["__pycache__", ".git", ".mypy_cache"],
        sort=False,
        maximum_depth=2,
    )
    logger.warning(folder.get_tree_repr())
    # for node in folder.descendants:
    #     logger.warning(node.displayable())
    # print(get_tree_repr(folder))

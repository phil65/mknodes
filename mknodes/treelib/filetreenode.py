from __future__ import annotations

from collections.abc import Callable
import logging
import pathlib

from typing import cast

from mknodes.data import treestyles
from mknodes.treelib import node


logger = logging.getLogger(__name__)


class FileTreeNode(node.Node):
    def __init__(self, path, **kwargs):
        self.path = path
        self.name = self.path.name
        super().__init__(**kwargs)

    def __repr__(self):
        return f"{self.name}/" if self.path.is_dir() else f"{self.name}"

    @classmethod
    def from_folder(
        cls,
        folder: pathlib.Path,
        *,
        predicate: Callable | None = None,
        exclude_folders: list[str] | None = None,
        sort: bool = True,
        max_items: int | None = None,
        maximum_depth: int | None = None,
        parent: FileTreeNode | None = None,
    ):
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
        return sum(i.path.is_folder() for i in self.descendants)

    def get_file_count(self) -> int:
        return sum(i.path.is_file() for i in self.descendants)

    def get_tree_repr(
        self,
        max_depth: int | None = None,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] | None = None,
        show_icon: bool = True,
    ) -> str:
        lines = []
        for pre_str, fill_str, _node in self.yield_tree(
            max_depth=max_depth,
            style=style or "ascii",
        ):
            _node = cast(FileTreeNode, _node)
            if show_icon and _node.path.is_dir():
                icon = "📁"
            elif show_icon:
                icon = "📄"
            else:
                icon = ""
            lines.append(f"{pre_str}{fill_str}{icon}{_node!r}")
        return repr(self) + "\n" + "\n".join(lines[1:])


if __name__ == "__main__":
    folder = FileTreeNode.from_folder(
        pathlib.Path(),
        exclude_folders=["__pycache__", ".git", ".mypy_cache"],
        sort=False,
        maximum_depth=2,
    )
    logger.warning(folder.get_tree_repr())
    # for node in folder.descendants:
    #     logger.warning(node.displayable())
    # print(get_tree_repr(folder))

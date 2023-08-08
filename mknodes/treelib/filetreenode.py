from __future__ import annotations

from collections.abc import Callable
import dataclasses
import logging
import os
import pathlib

from typing import TypeVar

from mknodes.treelib import node


logger = logging.getLogger(__name__)


@dataclasses.dataclass
class TreeStyle:
    identifier: str
    filename_prefix_middle: str
    filename_prefix_last: str
    parent_prefix_middle: str
    parent_prefix_last: str


default_style = TreeStyle("default", "├──", "└──", "    ", "│   ")
ansi_style = TreeStyle("ansi", "|-- ", "`-- ", "    ", "|   ")
ascii_style = TreeStyle("ascii", "|-- ", "+-- ", "    ", "|   ")
const_style = TreeStyle(
    "const",
    "\u251c\u2500\u2500 ",
    "\u2514\u2500\u2500 ",
    "    ",
    "\u2502   ",
)
const_bold_style = TreeStyle(
    "const_bold",
    "\u2523\u2501\u2501 ",
    "\u2517\u2501\u2501 ",
    "    ",
    "\u2503   ",
)
rounded_style = TreeStyle(
    "rounded",
    "\u251c\u2500\u2500 ",
    "\u2570\u2500\u2500 ",
    "    ",
    "\u2502   ",
)
double_style = TreeStyle(
    "double",
    "\u2560\u2550\u2550 ",
    "\u255a\u2550\u2550 ",
    "    ",
    "\u2551   ",
)
spaces_style = TreeStyle("spaces", "    ", "    ", "    ", "    ")


class FileTreeNode(node.Node):
    def __init__(self, path, is_last: bool = False, **kwargs):
        self.path = pathlib.Path(path)
        self.is_last = is_last
        self.sep = "/"
        super().__init__(**kwargs)

    def get_folder_count(self) -> int:
        return sum(i.path.is_dir() for i in self.descendants)

    def get_file_count(self) -> int:
        return sum(i.path.is_file() for i in self.descendants)

    @property
    def path_name(self) -> str:
        return str(self.path)

    def __repr__(self):
        return f"{self.path.name}/" if self.path.is_dir() else self.path.name

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
        if predicate:
            pred_fn = predicate
        else:

            def pred_fn(x):
                return True

        node = cls(folder, parent=parent)
        children = folder.iterdir()
        if sort:
            children = sorted(children, key=lambda s: str(s).lower())
        for path in children:
            if not pred_fn(path):
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

    def get_tree_repr(self, style: str = "something"):
        nodes = [self, *list(self.descendants)]
        return "\n".join(i.displayable(style) for i in nodes)

    def displayable(self, style: str = "something"):
        style = ascii_style
        if self.parent is None:
            return self.path_name

        _filename_prefix = (
            style.filename_prefix_last if self.is_last else style.filename_prefix_middle
        )
        parts = [f"{_filename_prefix!s} {self.path_name!s}"]
        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                (
                    style.parent_prefix_middle
                    if parent.is_last
                    else style.parent_prefix_last
                ),
            )
            parent = parent.parent

        return "".join(reversed(parts))


T = TypeVar("T", bound=FileTreeNode)


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

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
    filename_middle: str
    filename_last: str
    parent_middle: str
    parent_last: str


default_style = TreeStyle(
    identifier="default",
    filename_middle="├──",
    filename_last="└──",
    parent_middle="    ",
    parent_last="│   ",
)
ansi_style = TreeStyle(
    identifier="ansi",
    filename_middle="|-- ",
    filename_last="`-- ",
    parent_middle="    ",
    parent_last="|   ",
)
ascii_style = TreeStyle(
    identifier="ascii",
    filename_middle="|-- ",
    filename_last="+-- ",
    parent_middle="    ",
    parent_last="|   ",
)
const_style = TreeStyle(
    identifier="const",
    filename_middle="\u251c\u2500\u2500 ",
    filename_last="\u2514\u2500\u2500 ",
    parent_middle="    ",
    parent_last="\u2502   ",
)
const_bold_style = TreeStyle(
    identifier="const_bold",
    filename_middle="\u2523\u2501\u2501 ",
    filename_last="\u2517\u2501\u2501 ",
    parent_middle="    ",
    parent_last="\u2503   ",
)
rounded_style = TreeStyle(
    identifier="rounded",
    filename_middle="\u251c\u2500\u2500 ",
    filename_last="\u2570\u2500\u2500 ",
    parent_middle="    ",
    parent_last="\u2502   ",
)
double_style = TreeStyle(
    identifier="double",
    filename_middle="\u2560\u2550\u2550 ",
    filename_last="\u255a\u2550\u2550 ",
    parent_middle="    ",
    parent_last="\u2551   ",
)
spaces_style = TreeStyle(
    identifier="spaces",
    filename_middle="    ",
    filename_last="    ",
    parent_middle="    ",
    parent_last="    ",
)


class FileTreeNode(node.Node):
    def __init__(self, path, **kwargs):
        self.path = pathlib.Path(path)
        self.name = self.path.name
        self.type = "folder" if self.path.is_dir() else "file"
        self.sep = "/"
        super().__init__(**kwargs)

    def get_folder_count(self) -> int:
        return sum(i.type == "folder" for i in self.descendants)

    def get_file_count(self) -> int:
        return sum(i.type == "file" for i in self.descendants)

    @property
    def path_name(self) -> str:
        return str(self.path)

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

    def get_tree_repr(self, style: str = "something"):
        nodes = [self, *list(self.descendants)]
        return "\n".join(i.displayable(style) for i in nodes)

    def displayable(self, style: str = "something"):
        style = ascii_style
        if self.parent is None:
            return repr(self)
        _filename_prefix = (
            style.filename_last if not bool(self.right_sibling) else style.filename_middle
        )
        parts = [f"{_filename_prefix!s} {self!r}"]
        parent = self.parent
        while parent and parent.parent is not None:
            parts.append(
                (
                    style.parent_middle
                    if not bool(parent.right_sibling)
                    else style.parent_last
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

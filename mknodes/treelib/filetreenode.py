from __future__ import annotations

from collections.abc import Callable
import logging
import pathlib

from mknodes import treelib


logger = logging.getLogger(__name__)


class FileTreeNode(treelib.Node):
    def __init__(
        self,
        path: pathlib.Path | str,
        predicate: Callable | None = None,
        exclude: list[str] | None = None,
        sort: bool = True,
        maximum_depth: int | None = None,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.path = pathlib.Path(path)
        self.name = self.path.name
        self.predicate = predicate
        self.exclude = exclude
        self.sort = sort
        self.maximum_depth = maximum_depth

    def __eq__(self, other):
        if not type(other) == type(self):
            return False
        dct_1 = self.__dict__.copy()
        dct_1.pop("_parent")
        dct_2 = other.__dict__.copy()
        dct_2.pop("_parent")
        return dct_1 == dct_2

    def ls(self, path):
        return path.iterdir()

    @classmethod
    def is_dir(cls, item):
        return item.is_dir()

    @classmethod
    def get_name(cls, item):
        return item.name

    @property
    def children(self):
        if not self.is_dir(self.path):
            return []
        if self.maximum_depth is not None and self.maximum_depth < self.depth + 1:
            return []
        paths = []
        for i in self.ls(self.path):
            if self.exclude and self.is_dir(i) and self.get_name(i) in self.exclude:
                continue
            if self.predicate and not self.predicate(i):
                continue

            paths.append(i)
        if self.sort:
            paths = sorted(paths, key=lambda s: str(s).lower())
        return [FileTreeNode(i, parent=self) for i in paths]

    @children.setter
    def children(self, value):
        pass

    def __repr__(self):
        return self.path.name

    def get_folder_count(self) -> int:
        return sum(i.path.is_dir() for i in self.descendants)

    def get_file_count(self) -> int:
        return sum(i.path.is_file() for i in self.descendants)


if __name__ == "__main__":
    path = FileTreeNode(pathlib.Path("mknodes"))
    print(path.get_tree_repr())

    # @classmethod
    # def from_folder(
    #     cls,
    #     folder: os.PathLike,
    #     *,

    #     parent: FileTreeNode | None = None,
    # ):
    #     node = cls(folder, parent=parent)
    #     children = cls.get_children(folder)
    #     if sort:
    #         children = sorted(children, key=lambda s: str(s).lower())
    #     for path in children:

    #         elif maximum_depth is not None and maximum_depth < node.depth + 1:
    #             continue
    #         else:
    #             child = FileTreeNode.from_folder(
    #                 path,
    #                 parent=node,
    #                 predicate=predicate,
    #                 max_items=max_items,
    #                 maximum_depth=maximum_depth,
    #                 exclude=exclude,
    #             )
    #         if max_items is not None:
    #             if max_items > 0:
    #                 max_items -= 1
    #             else:
    #                 break

    #         node.append_child(child)
    #     return node

    # def get_tree_repr(self, style: str = "ascii"):
    #     # nodes = [self, *list(self.descendants)]
    #     # return "\n".join(i.displayable(style) for i in nodes)
    #     lines = [
    #         f"{(level - 1) * '    '} {node.displayable(style)}" for level, node in
    #     self.iter_nodes()
    #     ]
    #     return "\n".join(lines)

    # def displayable(self, style: str = "ascii"):
    #     style_obj = next(i for i in STYLES if i.identifier == style)
    #     if self.parent is None:
    #         return repr(self)
    #     _filename_prefix = (
    #         style_obj.filename_middle
    #         if bool(self.right_sibling)
    #         else style_obj.filename_last
    #     )
    #     parts = [f"{_filename_prefix!s} {self!r}"]
    #     parent = self.parent
    #     while parent and parent.parent is not None:
    #         if parent.is_last_child:
    #             parts.append(style_obj.parent_last)
    #         parent = parent.parent

    #     return "".join(reversed(parts))

    # def get_folder_count(self) -> int:
    #     return sum(i.type == "folder" for i in self.descendants)

    # def get_file_count(self) -> int:
    #     return sum(i.type == "file" for i in self.descendants)


# T = TypeVar("T", bound=FileTreeNode)


# if __name__ == "__main__":
# folder = FileTreeNode.from_folder(
#     ".",
#     exclude=["__pycache__", ".git", ".mypy_cache"],
#     sort=False,
#     maximum_depth=2,
# )
# logger.warning(folder.get_tree_repr())
# for node in folder.descendants:
#     logger.warning(node.displayable())
# print(get_tree_repr(folder))

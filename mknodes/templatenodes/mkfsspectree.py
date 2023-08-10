from __future__ import annotations

import logging

from typing import Literal, get_args

import fsspec

import mknodes

from mknodes import treelib


logger = logging.getLogger(__name__)


DirectoryTreeStyleStr = Literal["lines", "dash", "arrow", "spaces", "plus"]


class FsSpecTreeNode(treelib.FileTreeNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def children(self):
        return self.fs.ls(self.path)

    @classmethod
    def get_name(cls, item):
        return item["name"]

    @classmethod
    def is_dir(cls, item):
        return item["type"] == "directory"


class FsSpecTree(mknodes.MkDirectoryTree):
    """Node to display a fsspec path as a tree.

    Based on "fsspec" package

    """

    def __init__(self, protocol: str, storage_options: dict | None = None, **kwargs):
        self.set_protocol(protocol, **(storage_options or {}))
        super().__init__("", **kwargs)

    def set_protocol(self, protocol: str | fsspec.AbstractFileSystem, **kwargs):
        if isinstance(protocol, str):
            protocol = fsspec.filesystem(protocol, **kwargs)
        self.fs = protocol

    # @property
    # def text(self):
    #     node = FsSpecTreeNode.from_folder(
    #         fsspec.filesystem("github", org="phil65", repo="mknodes", path="/"),
    #         predicate=self.predicate,
    #         # exclude_folders=self.exclude_folders,
    #     )
    # return treelib.get_tree_repr(
    #     node,
    #     style=self.style or "rounded",
    #     max_depth=self.maximum_depth or 0,
    # )

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        for style in get_args(DirectoryTreeStyleStr):
            node = FsSpecTree("mknodes/manual", style=style)
            page += mknodes.MkReprRawRendered(node, header=f"### Style '{style}'")


if __name__ == "__main__":
    node = FsSpecTree("github", storage_options=dict(org="phil65", repo="mknodes"))
    print(node.to_markdown())

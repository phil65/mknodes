from __future__ import annotations

import os

import mknodes

from mknodes.plugin import buildbackend
from mknodes.utils import pathhelpers


class MarkdownBackend(buildbackend.BuildBackend):
    def __init__(
        self,
        directory: str | os.PathLike | None = None,
        extension: str = ".md",
    ):
        super().__init__(directory)
        self.extension = extension

    def _write_file(self, path: str | os.PathLike, content: str | bytes):
        target_path = (self.directory / path).with_suffix(self.extension)
        pathhelpers.write_file(content, target_path)

    def collect_from_root(self, node: mknodes.MkNode):
        all_files: dict[str, str | bytes] = node.resolved_virtual_files
        for des in node.descendants:
            all_files |= des.resolved_virtual_files
        self.write_files(all_files)


if __name__ == "__main__":
    cfg = MarkdownBackend()

from __future__ import annotations

import os
import pathlib
import re

import fsspec

from mknodes.utils import log


logger = log.get_logger(__name__)

_RFC_3986_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+\-+.]*://")


def is_fsspec_url(url: str | os.PathLike[str]) -> bool:
    """Returns true if the given URL looks like something fsspec can handle."""
    return (
        isinstance(url, str)
        and bool(_RFC_3986_PATTERN.match(url))
        and not url.startswith(("http://", "https://"))
    )


class FsSpecPath:
    def __init__(
        self,
        path: dict | str,
        fs: fsspec.AbstractFileSystem | str,
        **kwargs,
    ):
        filesystem = fsspec.filesystem(fs, **kwargs) if isinstance(fs, str) else fs
        match path:
            case dict():
                self.path = path
            case str() if filesystem:
                self.path = filesystem.info(path)
            case FsSpecPath():
                self.path = path.path
        self.fs = filesystem

    def __str__(self):
        return self.protocol_path

    def __repr__(self):
        return f"FsSpecPath({self.protocol_path!r})"

    def __truediv__(self, other):
        path = str(pathlib.Path(self.path["name"]) / other)
        return FsSpecPath(path, self.fs)

    @property
    def parent(self):
        path = str(pathlib.Path(self.path["name"]).parent)
        return FsSpecPath(path, self.fs)

    @property
    def name(self):
        return pathlib.Path(str(path)).name if (path := self.path["name"]) else ""

    @property
    def protocol_path(self) -> str:
        """Get protocol path for given index."""
        protocol = self.fs.protocol
        path = self.path["name"]
        return f"{protocol}://{path}"

    def iterdir(self):
        try:
            for i in self.fs.ls(self.path["name"], detail=True):
                yield FsSpecPath(i, self.fs)
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "Error fetching %s for protocol %s: %s",
                self.path["name"],
                self.fs.protocol,
                e,
            )
            return

    def read_text(self) -> str:
        with self.fs.open(self.protocol_path) as file:
            content = file.read()
            return content.decode() if isinstance(content, bytes) else content

    def is_file(self) -> bool:
        return self.path["type"] == "file"

    def is_dir(self) -> bool:
        return self.path["type"] == "directory"

    def exists(self) -> bool:
        return self.fs.exists(self.path["name"])

    def absolute(self):
        return self


if __name__ == "__main__":
    path = FsSpecPath("", "github", org="phil65", repo="mknodes")

    # from mknodes.treelib import filetreenode
    # folder = filetreenode.FileTreeNode.from_folder(
    #     path,
    #     exclude_folders=["__pycache__", ".git", ".mypy_cache"],
    #     sort=False,
    #     maximum_depth=2,
    # )
    # logger.warning(folder.get_tree_repr())

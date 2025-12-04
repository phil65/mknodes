from __future__ import annotations

import functools
from typing import TYPE_CHECKING

from upathtools import to_upath

from mknodes.utils import log
from mknodes.utils.downloadhelpers import download


if TYPE_CHECKING:
    import os

    import upath
    from upath.types import JoinablePathLike


logger = log.get_logger(__name__)


def find_cfg_for_folder(
    filename: JoinablePathLike,
    folder: JoinablePathLike = ".",
) -> upath.UPath | None:
    """Search for a file with given name in folder and its parent folders.

    Args:
        filename: File to search
        folder: Folder to start searching from
    """
    if folder and str(folder) != ".":
        path = to_upath(folder).resolve() / str(filename)
    else:
        path = to_upath(filename).resolve()
    while len(path.parts) > 1:
        path = path.parent
        if (file := path / str(filename)).exists():
            return file
    return None


@functools.cache
def load_file_cached(path: str | os.PathLike[str]) -> str:
    return download(str(path)).decode()


if __name__ == "__main__":
    file = find_cfg_for_folder("github://phil65:mknodes@main/docs/icons.jinja")

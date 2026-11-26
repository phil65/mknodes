import functools
import os
import re
from typing import TYPE_CHECKING
from urllib import parse

from upathtools import to_upath

from mknodes.utils import log


if TYPE_CHECKING:
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


_DRIVE = re.compile(r"^[a-zA-Z]:[\\/]")


def is_remote(path: str | os.PathLike[str]) -> bool:
    """Return whether given path is a remote URL (http(s) or another fsspec protocol).

    Local paths and `file://` URLs are not remote.
    """
    if not isinstance(path, str) or _DRIVE.match(path):
        return False
    return parse.urlsplit(path).scheme not in {"", "file", "local"}


def load_file(path: str | os.PathLike[str]) -> str:
    """Return the text of a local file or of a remote URL (any fsspec protocol).

    Remote files are external inputs: during a build they come from the inputs store
    (kind `file`, pinned in the lock file), see `mknodes.inputs`.
    """
    if is_remote(path):
        from mknodes import inputs

        return inputs.get_input("file", url=str(path))
    return to_upath(os.fspath(path)).read_bytes().decode()


def load_bytes(path: str | os.PathLike[str], **storage_options: object) -> bytes:
    """Return the bytes of a local file or of a remote URL (inputs store kind `binary_file`)."""
    if is_remote(path) and not storage_options:
        import base64

        from mknodes import inputs

        return base64.b64decode(inputs.get_input("binary_file", url=str(path)))
    return to_upath(os.fspath(path), **storage_options).read_bytes()


@functools.cache
def _load_local_cached(path: str) -> str:
    return to_upath(path).read_bytes().decode()


def load_file_cached(path: str | os.PathLike[str]) -> str:
    """Like `load_file`, local files are read once per process."""
    if is_remote(path):
        return load_file(path)
    return _load_local_cached(os.fspath(path))


if __name__ == "__main__":
    file = find_cfg_for_folder("github://phil65:mknodes@main/docs/icons.jinja")

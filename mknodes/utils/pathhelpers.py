from __future__ import annotations

import functools
import os
import pathlib
import shutil
from typing import TYPE_CHECKING

import upath

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Mapping


logger = log.get_logger(__name__)


def fsspec_copy(
    source_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    exist_ok: bool = True,
):
    """Copy source_path to output_path, making sure any parent directories exist.

    The output_path may be a directory.

    Arguments:
        source_path: File to copy
        output_path: path where file should get copied to.
        exist_ok: Whether exception should be raised in case stuff would get overwritten
    """
    import fsspec

    if isinstance(source_path, upath.UPath):
        src = fsspec.FSMap(source_path.path, source_path.fs)
    else:
        src = fsspec.get_mapper(str(source_path))
    if isinstance(output_path, upath.UPath):
        target = fsspec.FSMap(output_path.path, output_path.fs)
    else:
        target = fsspec.get_mapper(str(output_path))
    if not exist_ok and any(key in target for key in src):
        msg = "cannot overwrite if exist_ok is set to False"
        raise RuntimeError(msg)
    for k in src:
        target[k] = src[k]


def copy(
    source_path: str | os.PathLike[str],
    output_path: str | os.PathLike[str],
    exist_ok: bool = True,
):
    """Copy source_path to output_path, making sure any parent directories exist.

    The output_path may be a directory.

    Arguments:
        source_path: File to copy
        output_path: path where file should get copied to.
        exist_ok: Whether exception should be raised in case stuff would get overwritten
    """
    output_p = upath.UPath(output_path)
    source_p = upath.UPath(source_path)
    output_p.parent.mkdir(parents=True, exist_ok=exist_ok)
    if source_p.is_dir():
        if output_p.is_dir():
            msg = "Cannot copy folder to file!"
            raise RuntimeError(msg)
        shutil.copytree(source_p, output_p, dirs_exist_ok=exist_ok)
    else:
        if output_p.is_dir():
            output_p /= source_p.name
        shutil.copyfile(source_p, output_p)


def clean_directory(
    directory: str | os.PathLike[str], remove_hidden: bool = False
) -> None:
    """Remove the content of a directory recursively but not the directory itself."""
    folder_to_remove = upath.UPath(directory)
    if not folder_to_remove.exists():
        return
    for entry in folder_to_remove.iterdir():
        if entry.name.startswith(".") and not remove_hidden:
            continue
        path = folder_to_remove / entry
        if path.is_dir():
            shutil.rmtree(path, True)
        else:
            path.unlink()


def write_file(content: str | bytes, output_path: str | os.PathLike[str]):
    """Write content to output_path, making sure any parent directories exist.

    Arguments:
        content: Content to write
        output_path: path where file should get written to.
    """
    output_p = upath.UPath(output_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    encoding = None if "b" in mode else "utf-8"
    with output_p.open(mode=mode, encoding=encoding) as f:  # type: ignore[call-overload]
        f.write(content)


def write_files(mapping: Mapping[str | os.PathLike[str], str | bytes]):
    """Write a mapping of filename-to-content to disk.

    Arguments:
        mapping: {"path/to/file.ext": b"content", ...} - style mapping
    """
    for k, v in mapping.items():
        write_file(v, k)


def find_cfg_for_folder(
    filename: str | pathlib.Path,
    folder: os.PathLike[str] | str = ".",
) -> pathlib.Path | None:
    """Search for a file with given name in folder and its parent folders.

    Arguments:
        filename: File to search
        folder: Folder to start searching from
    """
    if folder and folder != ".":
        path = upath.UPath(folder).absolute() / filename
    else:
        path = upath.UPath(filename).absolute()
    while len(path.parts) > 1:
        path = path.parent
        if (file := path / filename).exists():
            return file
    return None


@functools.cache
def load_file_cached(path: str | os.PathLike[str]) -> str:
    if "://" in str(path):
        return fsspec_get(str(path))
    return pathlib.Path(path).read_text(encoding="utf-8")


def download_from_github(
    org: str,
    repo: str,
    path: str | os.PathLike[str],
    destination: str | os.PathLike[str],
    username: str | None = None,
    token: str | None = None,
    recursive: bool = False,
):
    import fsspec

    token = token or os.environ.get("GITHUB_TOKEN")
    if token and not username:
        token = None
    dest = upath.UPath(destination)
    dest.mkdir(exist_ok=True, parents=True)
    fs = fsspec.filesystem("github", org=org, repo=repo)
    logger.info("Copying files from Github: %s", path)
    files = fs.ls(str(path))
    fs.get(files, dest.as_posix(), recursive=recursive)


@functools.cache
def fsspec_get(path: str) -> str:
    import fsspec

    with fsspec.open(path) as file:
        return file.read().decode()


if __name__ == "__main__":
    file = find_cfg_for_folder("github://phil65:mknodes@main/docs/icons.jinja")

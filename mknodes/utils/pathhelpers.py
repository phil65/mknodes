from __future__ import annotations

from collections.abc import Mapping
import functools
import os
import pathlib
import posixpath
import re
import shutil

import upath

from upath import core, registry

from mknodes.utils import log


_RFC_3986_PATTERN = re.compile(r"^[A-Za-z][A-Za-z0-9+\-+.]*://")

logger = log.get_logger(__name__)


class _GitHubAccessor(core._FSSpecAccessor):
    """FSSpecAccessor for GitHub."""

    def _format_path(self, path: core.UPath) -> str:
        """Remove the leading slash from the path."""
        return path._path.lstrip("/")


class GitHubPath(core.UPath):
    """GitHubPath supporting the fsspec.GitHubFileSystem."""

    _default_accessor = _GitHubAccessor


cls_path = "mknodes.utils.pathhelpers.GitHubPath"
registry._Registry.known_implementations["github"] = cls_path


def fsspec_copy(
    source_path: str | os.PathLike,
    output_path: str | os.PathLike,
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


#
def copy(
    source_path: str | os.PathLike,
    output_path: str | os.PathLike,
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
            output_p = output_p / source_p.name
        shutil.copyfile(source_p, output_p)


def clean_directory(directory: str | os.PathLike, remove_hidden: bool = False) -> None:
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


def write_file(content: str | bytes, output_path: str | os.PathLike):
    """Write content to output_path, making sure any parent directories exist.

    Arguments:
        content: Content to write
        output_path: path where file should get written to.
    """
    output_p = upath.UPath(output_path)
    output_p.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    encoding = None if "b" in mode else "utf-8"
    with output_p.open(mode=mode, encoding=encoding) as f:
        f.write(content)


def write_files(mapping: Mapping[str | os.PathLike, str | bytes]):
    """Write a mapping of filename-to-content to disk.

    Arguments:
        mapping: {"path/to/file.ext": b"content", ...} - style mapping
    """
    for k, v in mapping.items():
        write_file(v, k)


# deprecated
def find_file_in_folder_or_parent(
    filename: str | pathlib.Path,
    folder: os.PathLike | str = ".",
) -> pathlib.Path | None:
    return find_cfg_for_folder(filename, folder)


def find_cfg_for_folder(
    filename: str | pathlib.Path,
    folder: os.PathLike | str = ".",
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
def load_file_cached(path: str | os.PathLike) -> str:
    if "://" in str(path):
        return fsspec_get(str(path))
    return pathlib.Path(path).read_text(encoding="utf-8")


def is_fsspec_url(url: str | os.PathLike[str]) -> bool:
    """Returns true if the given URL looks like something fsspec can handle."""
    return (
        isinstance(url, str)
        and bool(_RFC_3986_PATTERN.match(url))
        and not url.startswith(("http://", "https://"))
    )


def download_from_github(
    org: str,
    repo: str,
    path: str | os.PathLike,
    destination: str | os.PathLike,
    username=None,
    token=None,
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


@functools.lru_cache
def _get_norm_url(path: str) -> tuple[str, int]:
    from urllib.parse import urlsplit

    if not path:
        path = "."
    elif "\\" in path:
        logger.warning(
            "Path %r uses OS-specific separator '\\'. "
            "That will be unsupported in a future release. Please change it to '/'.",
            path,
        )
        path = path.replace("\\", "/")
    # Allow links to be fully qualified URLs
    parsed = urlsplit(path)
    if parsed.scheme or parsed.netloc or path.startswith(("/", "#")):
        return path, -1

    # Relative path - preserve information about it
    norm = posixpath.normpath(path) + "/"
    relative_level = 0
    while norm.startswith("../", relative_level * 3):
        relative_level += 1
    return path, relative_level


def normalize_url(path: str, url: str | None = None, base: str = "") -> str:
    """Return a URL relative to the given page or using the base."""
    path, relative_level = _get_norm_url(path)
    if relative_level == -1:
        return path
    if url is not None:
        result = relative_url(url, path)
        if relative_level > 0:
            result = "../" * relative_level + result
        return result

    return posixpath.join(base, path)


def relative_url(url_a: str, url_b: str) -> str:
    """Compute the relative path from URL A to URL B.

    Arguments:
        url_a: URL A.
        url_b: URL B.

    Returns:
        The relative URL to go from A to B.
    """
    parts_a = url_a.split("/")
    if "#" in url_b:
        url_b, anchor = url_b.split("#", 1)
    else:
        anchor = None
    parts_b = url_b.split("/")

    # remove common left parts
    while parts_a and parts_b and parts_a[0] == parts_b[0]:
        parts_a.pop(0)
        parts_b.pop(0)

    # go up as many times as remaining a parts' depth
    levels = len(parts_a) - 1
    parts_relative = [".."] * levels + parts_b
    relative = "/".join(parts_relative)
    return f"{relative}#{anchor}" if anchor else relative


if __name__ == "__main__":
    file = find_file_in_folder_or_parent("github://phil65:mknodes@main/docs/icons.jinja")

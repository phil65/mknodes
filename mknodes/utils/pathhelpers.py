from __future__ import annotations

import logging
import os
import pathlib
import shutil


logger = logging.getLogger(__name__)


def copy_file(source_path: str | os.PathLike, output_path: str | os.PathLike):
    """Copy source_path to output_path, making sure any parent directories exist.

    The output_path may be a directory.
    """
    output_path = pathlib.Path(output_path)
    source_path = pathlib.Path(source_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if output_path.is_dir():
        output_path = output_path / source_path.name
    shutil.copyfile(source_path, output_path)


def write_file(content: str | bytes, output_path: str | os.PathLike):
    """Write content to output_path, making sure any parent directories exist."""
    output_path = pathlib.Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    mode = "wb" if isinstance(content, bytes) else "w"
    with output_path.open(mode) as f:
        f.write(content)


def find_file_in_folder_or_parent(
    filename: str | pathlib.Path,
    folder: os.PathLike | str = ".",
) -> pathlib.Path | None:
    """Search for a file with given name in folder and its parent folders.

    Arguments:
        filename: File to search
        folder: Folder to start searching from
    """
    path = pathlib.Path(folder).absolute()
    while not (path / filename).exists() and len(path.parts) > 1:
        path = path.parent
    return file if (file := (path / filename)).exists() else None


def get_material_icon_path(icon: str) -> pathlib.Path:
    import material

    path = pathlib.Path(next(iter(material.__path__)))
    return path / ".icons" / f"{icon}.svg"


if __name__ == "__main__":
    file = find_file_in_folder_or_parent("pyproject.toml")
    print(file)

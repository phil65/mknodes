# File taken from mkdocs-gen-files, credits to the authors.

from __future__ import annotations

import collections

from collections.abc import MutableMapping
import os
import os.path
import pathlib
import shutil
from typing import IO, ClassVar

from mkdocs.config import Config, load_config
from mkdocs.structure.files import File, Files


def file_sort_key(f: File):
    parts = pathlib.PurePath(f.src_path).parts
    return tuple(
        chr(f.name != "index" if i == len(parts) - 1 else 2) + p
        for i, p in enumerate(parts)
    )


class FilesEditor:
    config: Config  # https://www.mkdocs.org/user-guide/plugins/#config)
    directory: str  # https://www.mkdocs.org/user-guide/configuration/#docs_dir
    _current: ClassVar[FilesEditor | None] = None
    _default: ClassVar[FilesEditor | None] = None

    def __init__(self, files: Files, config: Config, directory: str | None = None):
        files_map = {pathlib.PurePath(f.src_path).as_posix(): f for f in files}
        self._files: MutableMapping[str, File] = collections.ChainMap({}, files_map)
        self.config = config
        self.directory = directory or config["docs_dir"]

    def __enter__(self):
        type(self)._current = self
        return self

    def __exit__(self, *exc):
        type(self)._current = None

    @classmethod
    def current(cls) -> FilesEditor:
        """The instance of FilesEditor associated with the currently ongoing MkDocs build.

        If used as part of a MkDocs build (*gen-files* plugin), it's an instance using
        virtual files that feed back into the build.

        If not, this still tries to load the MkDocs config to find out the *docs_dir*, and
        then actually performs any file writes that happen via `.open()`.

        This is global (not thread-safe).
        """
        if cls._current:
            return cls._current
        if not cls._default:
            config = load_config("mkdocs.yml")
            config["plugins"].run_event("config", config)
            cls._default = FilesEditor(Files([]), config)
        return cls._default

    @property
    def files(self) -> Files:
        """Access the files as they currently are, as a MkDocs [Files][] collection.

        [Files]: https://github.com/mkdocs/mkdocs/blob/master/mkdocs/structure/files.py
        """
        files = sorted(self._files.values(), key=file_sort_key)
        return Files(files)

    def open(  # noqa: A003
        self,
        name: str,
        mode,
        buffering=-1,
        encoding=None,
        **kwargs,
    ) -> IO:
        """Open a file under `docs_dir` virtually.

        This function, is just an `open()` which pretends that it is running under
        [docs_dir](https://www.mkdocs.org/user-guide/configuration/#docs_dir)
        (*docs/* by default), but write operations don't affect the actual files
        when running as part of a MkDocs build, but they do become part of the site build.
        """
        path = self._get_file(name, new="w" in mode)
        if encoding is None and "b" not in mode:
            encoding = "utf-8"
        return open(path, mode, buffering, encoding, **kwargs)  # noqa: PTH123 SIM115

    def _get_file(self, name: str, new: bool = False) -> str:
        # sourcery skip: extract-duplicate-method
        new_f = File(
            name,
            src_dir=self.directory,
            dest_dir=self.config["site_dir"],
            use_directory_urls=self.config["use_directory_urls"],
        )
        new_f.generated_by = "mknodes"  # type: ignore
        normname = pathlib.PurePath(name).as_posix()
        dir_name = os.path.dirname(new_f.abs_src_path)  # noqa: PTH120
        if new or normname not in self._files:
            os.makedirs(dir_name, exist_ok=True)  # noqa: PTH103
            self._files[normname] = new_f
            return new_f.abs_src_path

        f = self._files[normname]
        if f.abs_src_path != new_f.abs_src_path:
            os.makedirs(dir_name, exist_ok=True)  # noqa: PTH103
            self._files[normname] = new_f
            shutil.copyfile(f.abs_src_path, new_f.abs_src_path)
            return new_f.abs_src_path

        return f.abs_src_path

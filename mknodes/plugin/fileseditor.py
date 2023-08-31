# File taken from mkdocs-gen-files, credits to the authors.

from __future__ import annotations

import collections
import os
import pathlib
import shutil

from typing import IO, TYPE_CHECKING, ClassVar

from mkdocs.structure.files import Files

from mknodes import mkdocsconfig


if TYPE_CHECKING:
    from mkdocs.structure.files import File


def file_sort_key(f: File):
    parts = pathlib.PurePath(f.src_path).parts
    return tuple(
        chr(f.name != "index" if i == len(parts) - 1 else 2) + p
        for i, p in enumerate(parts)
    )


class FilesEditor:
    _current: ClassVar[FilesEditor | None] = None
    _default: ClassVar[FilesEditor | None] = None

    def __init__(
        self,
        files: Files,
        config: mkdocsconfig.Config,
        directory: str | os.PathLike | None = None,
    ):
        files_map = {pathlib.PurePath(f.src_path).as_posix(): f for f in files}
        self._files: collections.ChainMap[str, File] = collections.ChainMap({}, files_map)
        self.config = config
        self.directory = str(directory or config.docs_dir)

    def __enter__(self):
        type(self)._current = self
        return self

    def __exit__(self, *exc):
        type(self)._current = None

    @classmethod
    def current(cls) -> FilesEditor:
        """The instance of FilesEditor associated with the currently ongoing MkDocs build.

        If used as part of a MkDocs build, it's an instance using
        virtual files that feed back into the build.

        If not, this still tries to load the MkDocs config to find out the *docs_dir*, and
        then actually performs any file writes that happen via `.open()`.

        This is global (not thread-safe).
        """
        if cls._current:
            return cls._current
        if not cls._default:
            config = mkdocsconfig.Config()
            config.plugins.run_event("config", config._config)
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
        buffering: int = -1,
        encoding: str | None = None,
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
        return path.open(mode, buffering, encoding, **kwargs)  # noqa: SIM115

    def _get_file(self, name: str, new: bool = False) -> pathlib.Path:
        # sourcery skip: extract-duplicate-method
        new_f = self.config.get_file(name, src_dir=self.directory)
        normname = pathlib.PurePath(name).as_posix()
        new_path = pathlib.Path(new_f.abs_src_path)
        if new or normname not in self._files:
            new_path.parent.mkdir(exist_ok=True, parents=True)
            self._files[normname] = new_f
            return new_path

        f = self._files[normname]
        source_path = pathlib.Path(f.abs_src_path)
        if source_path != new_path:
            new_path.parent.mkdir(exist_ok=True, parents=True)
            self._files[normname] = new_f
            shutil.copyfile(source_path, new_path)
            return new_path

        return source_path

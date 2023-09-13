from __future__ import annotations

import collections
import os
import pathlib

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure import files as files_

from mknodes import mkdocsconfig
from mknodes.plugin import buildbackend, mkdocsbuilder, mkdocshelpers
from mknodes.utils import pathhelpers


logger = get_plugin_logger(__name__)


class MkDocsBackend(buildbackend.BuildBackend):
    def __init__(
        self,
        files: files_.Files | None = None,
        config: mkdocsconfig.Config | MkDocsConfig | str | os.PathLike | None = None,
        directory: str | os.PathLike | None = None,
    ):
        match config:
            case mkdocsconfig.Config():
                self._config = config._config
            case MkDocsConfig():
                self._config = config
            case _:
                self._config = mkdocsconfig.Config(config)._config
        super().__init__(directory)
        files_map = {pathlib.PurePath(f.src_path).as_posix(): f for f in files or []}
        self._mk_files: collections.ChainMap[str, files_.File] = collections.ChainMap(
            {},
            files_map,
        )
        self.builder = mkdocsbuilder.MkDocsBuilder(self._config)

    @property
    def files(self) -> files_.Files:
        """Access the files as they currently are, as a MkDocs [Files][] collection.

        [Files]: https://github.com/mkdocs/mkdocs/blob/master/mkdocs/structure/files.py
        """
        files = sorted(self._mk_files.values(), key=mkdocshelpers.file_sorter)
        return files_.Files(files)

    def _write_file(self, path: str | os.PathLike, content: str | bytes):
        src_path = self._get_path(path)
        pathhelpers.write_file(content, src_path)
        md_path = (pathlib.Path("src") / path).with_suffix(".original")
        pathhelpers.write_file(content, self._config.site_dir / md_path)

    def _get_path(self, path: str | os.PathLike) -> pathlib.Path:
        # sourcery skip: extract-duplicate-method
        normname = pathlib.PurePath(path).as_posix()
        new_f = self.builder.get_file(path, src_dir=self.directory)
        new_path = pathlib.Path(new_f.abs_src_path)
        if normname not in self._mk_files:
            new_path.parent.mkdir(exist_ok=True, parents=True)
            self._mk_files[normname] = new_f
            return new_path

        f = self._mk_files[normname]
        source_path = pathlib.Path(f.abs_src_path)
        if source_path != new_path:
            self._mk_files[normname] = new_f
            pathhelpers.copy(source_path, new_path)
            return new_path

        return source_path


if __name__ == "__main__":
    backend = MkDocsBackend()

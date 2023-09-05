from __future__ import annotations

import collections

from collections.abc import Mapping
import os
import pathlib
import shutil

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure import files as files_, nav, pages

from mknodes import mkdocsconfig


logger = get_plugin_logger(__name__)


class MkDocsBuilder:
    def __init__(
        self,
        files: files_.Files | None = None,
        config: mkdocsconfig.Config | MkDocsConfig | str | os.PathLike | None = None,
        directory: str | os.PathLike | None = None,
    ):
        files_map = {pathlib.PurePath(f.src_path).as_posix(): f for f in files or []}
        self._files: collections.ChainMap[str, files_.File] = collections.ChainMap(
            {},
            files_map,
        )
        match config:
            case mkdocsconfig.Config():
                self._config = config._config
            case MkDocsConfig():
                self._config = config
            case _:
                self._config = mkdocsconfig.Config(config)._config
        self.directory = str(directory or self._config.docs_dir)

    def get_file(
        self,
        path: str | os.PathLike,
        src_dir: str | os.PathLike | None = None,
        dest_dir: str | os.PathLike | None = None,
        inclusion_level: files_.InclusionLevel = files_.InclusionLevel.UNDEFINED,
    ) -> files_.File:
        """Return a MkDocs File for given path.

        Arguments:
            path: path to get a File object for (relative to src_dir)
            src_dir: Source directory. If None, docs_dir is used.
            dest_dir: Target directory. If None, site_dir is used.
            inclusion_level: Inclusion level of new file
        """
        new_f = files_.File(
            str(path),
            src_dir=str(src_dir) if src_dir else self._config.docs_dir,
            dest_dir=str(dest_dir) if dest_dir else self._config.site_dir,
            use_directory_urls=self._config.use_directory_urls,
            inclusion=inclusion_level,
        )
        new_f.generated_by = "mknodes"  # type: ignore
        return new_f

    def get_section_page(
        self,
        title: str,
        path: str | os.PathLike,
        children: list[pages.Page | nav.Section | nav.Link],
        inclusion_level: files_.InclusionLevel = files_.InclusionLevel.UNDEFINED,
    ) -> pages.Page:
        import mkdocs_section_index

        file = self.get_file(path, inclusion_level=inclusion_level)
        return mkdocs_section_index.SectionPage(
            title=title,
            file=file,
            config=self._config,
            children=children,
        )

    def get_page(
        self,
        title: str,
        path: str | os.PathLike,
        inclusion_level: files_.InclusionLevel = files_.InclusionLevel.UNDEFINED,
    ) -> pages.Page:
        file = self.get_file(path, inclusion_level=inclusion_level)
        return pages.Page(title, file, self._config)

    def get_nav(self, file_list: list[files_.File]) -> nav.Navigation:
        files = files_.Files(file_list)
        return nav.get_navigation(files, self._config)

    @property
    def files(self) -> files_.Files:
        """Access the files as they currently are, as a MkDocs [Files][] collection.

        [Files]: https://github.com/mkdocs/mkdocs/blob/master/mkdocs/structure/files.py
        """

        def file_sort_key(f: files_.File):
            parts = pathlib.PurePath(f.src_path).parts
            return tuple(
                chr(f.name != "index" if i == len(parts) - 1 else 2) + p
                for i, p in enumerate(parts)
            )

        files = sorted(self._files.values(), key=file_sort_key)
        return files_.Files(files)

    def write(self, path: str | os.PathLike, content: str | bytes):
        mode = "w" if isinstance(content, str) else "wb"
        path = self._get_path(os.fspath(path), new="w" in mode)
        encoding = None if "b" in mode else "utf-8"
        logger.info("Writing file to %s", path)
        with path.open(mode=mode, encoding=encoding) as file:
            file.write(content)

    def write_files(self, dct: Mapping[str, str | bytes]):
        """Write a mapping of {filename: file_content} to build directory."""
        for k, v in dct.items():
            self.write(k, v)

    def _get_path(self, name: str, new: bool = False) -> pathlib.Path:
        # sourcery skip: extract-duplicate-method
        new_f = self.get_file(name, src_dir=self.directory)
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


if __name__ == "__main__":
    cfg = MkDocsBuilder()

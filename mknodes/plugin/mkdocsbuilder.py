from __future__ import annotations

import os

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.plugins import get_plugin_logger
from mkdocs.structure import files as files_, nav, pages

from mknodes import mkdocsconfig
from mknodes.plugin import buildbackend


logger = get_plugin_logger(__name__)


class MkDocsBuilder(buildbackend.BuildBackend):
    def __init__(
        self,
        config: mkdocsconfig.Config | MkDocsConfig | str | os.PathLike | None = None,
    ):
        match config:
            case mkdocsconfig.Config():
                self._config = config._config
            case MkDocsConfig():
                self._config = config
            case _:
                self._config = mkdocsconfig.Config(config)._config

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
            os.fspath(path),
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


if __name__ == "__main__":
    cfg = MkDocsBuilder()

from __future__ import annotations

import logging
import os

from typing import TYPE_CHECKING, Generic, TypeVar

from mknodes import mkdocsconfig, mknav
from mknodes.info import folderinfo
from mknodes.pages import pagetemplate
from mknodes.theme import theme as theme_
from mknodes.utils import helpers, linkprovider, reprhelpers


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


logger = logging.getLogger(__name__)


T = TypeVar("T", bound=theme_.Theme)


class Project(Generic[T]):
    """MkNodes Project."""

    def __init__(
        self,
        theme: T,
        config: MkDocsConfig | None = None,
        repo_path: str | os.PathLike | None = None,
    ):
        self.linkprovider = linkprovider.LinkProvider(config, include_stdlib=True)
        self.config: mkdocsconfig.Config = mkdocsconfig.Config(config)
        self.theme: T = theme
        self.templates = self.theme.templates
        self.error_page: pagetemplate.PageTemplate = self.templates["404.html"]
        if helpers.is_url(str(repo_path)):
            self.folderinfo = folderinfo.FolderInfo.clone_from(str(repo_path))
        else:
            self.folderinfo = folderinfo.FolderInfo(repo_path)
        self._root: mknav.MkNav | None = None

    def __repr__(self):
        return reprhelpers.get_repr(self, repo_path=self.folderinfo.path)

    @classmethod
    def for_mknodes(cls) -> Project:
        config = mkdocsconfig.Config()
        theme = theme_.Theme.get_theme(config)
        return cls(config=config._config, theme=theme)

    @property
    def info(self):
        return self.folderinfo.info

    @property
    def package_name(self) -> str:
        return self.folderinfo.package_name

    def get_root(self, **kwargs) -> mknav.MkNav:
        self._root = mknav.MkNav(project=self, **kwargs)
        return self._root

    def set_root(self, nav: mknav.MkNav):
        self._root = nav
        nav.associated_project = self

    def all_files(self) -> dict[str, str | bytes]:
        files = self._root.all_virtual_files() if self._root else {}
        return files | self.theme.get_files()

    def all_markdown_extensions(self) -> dict[str, dict]:
        extensions = self._root.all_markdown_extensions() if self._root else {}
        return self.theme.adapt_extensions(extensions)

    def aggregate_info(self):
        return self.folderinfo.aggregate_info() | self.theme.aggregate_info()


if __name__ == "__main__":
    project = Project.for_mknodes()
    print(project)

from __future__ import annotations

import logging
import re
import types

from typing import TYPE_CHECKING, Generic, TypeVar

from mknodes import mkdocsconfig, mknav
from mknodes.info import folderinfo, packageinfo
from mknodes.pages import pagetemplate
from mknodes.theme import theme as theme_
from mknodes.utils import helpers, linkprovider


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig


logger = logging.getLogger(__name__)

GITHUB_REGEX = re.compile(
    r"(?:http?:\/\/|https?:\/\/)?"
    r"(?:www\.)?"
    r"github\.com\/"
    r"(?:\/*)"
    r"([\w\-\.]*)\/"
    r"([\w\-]*)"
    r"(?:\/|$)?"  # noqa: COM812
)

T = TypeVar("T", bound=theme_.Theme)


class Project(Generic[T]):
    """MkNodes Project."""

    def __init__(
        self,
        theme: T,
        module: types.ModuleType | None = None,
        config: MkDocsConfig | None = None,
    ):
        self._module = module
        self.linkprovider = linkprovider.LinkProvider(config, include_stdlib=True)
        self.config: mkdocsconfig.Config = mkdocsconfig.Config(config)
        self.theme: T = theme
        self.templates = self.theme.templates
        self.error_page: pagetemplate.PageTemplate = self.templates["404.html"]
        self.folderinfo = folderinfo.FolderInfo()
        self._root: mknav.MkNav | None = None

    @classmethod
    def for_mknodes(cls) -> Project:
        import mknodes

        config = mkdocsconfig.Config()
        theme = theme_.Theme.get_theme(config)
        return cls(module=mknodes, config=config._config, theme=theme)

    @property
    def info(self):
        return packageinfo.get_info(self.package_name)

    @property
    def module(self) -> types.ModuleType:
        if not self._module:
            msg = "No module set"
            raise RuntimeError(msg)
        return self._module

    @module.setter
    def module(self, value):
        self._module = value

    @property
    def package_name(self):
        return self.module.__name__

    def __repr__(self):
        return helpers.get_repr(self, module=self.module)

    @property
    def repository_url(self) -> str | None:
        return url if (url := self.config.repo_url) else self.info.repository_url

    @property
    def repository_username(self) -> str | None:
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(1)
        return None

    @property
    def repository_name(self) -> str | None:
        if match := GITHUB_REGEX.match(self.repository_url or ""):
            return match.group(2)
        return None

    def get_root(self, **kwargs) -> mknav.MkNav:
        self._root = mknav.MkNav(project=self, **kwargs)
        return self._root

    def all_files(self) -> dict[str, str | bytes]:
        files = self._root.all_virtual_files() if self._root else {}
        return files | self.theme.get_files()

    def all_markdown_extensions(self) -> dict[str, dict]:
        extensions = self._root.all_markdown_extensions() if self._root else {}
        return self.theme.adapt_extensions(extensions)

    def aggregate_info(self):
        infos = dict(
            repository_name=self.repository_name,
            repository_username=self.repository_username,
            repository_url=self.repository_url,
        )
        return infos | self.info.metadata.json | self.theme.aggregate_info()


if __name__ == "__main__":
    project = Project.for_mknodes()
    print(project)

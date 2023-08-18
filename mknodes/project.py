from __future__ import annotations

import logging
import re
import types

from typing import TYPE_CHECKING

from mknodes import mkdocsconfig, mknav
from mknodes.basenodes import mknode
from mknodes.cssclasses import rootcss, templateblocks
from mknodes.data import datatypes, taskrunners, tools
from mknodes.utils import helpers, packageinfo, pyproject


if TYPE_CHECKING:
    from mkdocs.config.defaults import MkDocsConfig
    from mkdocs.structure.files import Files

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


class Project:
    """MkNodes Project."""

    def __init__(
        self,
        module: types.ModuleType | None = None,
        config: MkDocsConfig | None = None,
        files: Files | None = None,
    ):
        self._module = module
        self.config = mkdocsconfig.Config(config)
        self.files = files
        self.root_css = rootcss.RootCSS()
        md = self.config.get_markdown_instance()
        self.main_template = templateblocks.PageTemplate(md, filename="main.html")
        self.pyproject = pyproject.PyProject()
        self._root: mknav.MkNav | None = None
        self._foreground_color = None

    @property
    def announcement_bar(self):
        return self.main_template.announcement_bar

    @announcement_bar.setter
    def announcement_bar(self, value):
        if isinstance(value, mknode.MkNode):
            value._associated_project = self
        self.main_template.announcement_bar = value

    @property
    def package_repos(self):
        return self.pyproject.package_repos

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
    def commit_types(self):
        return self.pyproject.allowed_commit_types

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

    @property
    def tools(self) -> list[tools.Tool]:
        return [t for t in tools.TOOLS.values() if t.is_used()]

    @property
    def task_runners(self) -> list[taskrunners.TaskRunner]:
        """Return list of task runners used by this project."""
        return [
            runner
            for runner in taskrunners.TASK_RUNNERS.values()
            if any(helpers.find_file_in_folder_or_parent(i) for i in runner.filenames)
        ]

    def all_files(self) -> dict[str, str | bytes]:
        files = self._root.all_virtual_files() if self._root else {}
        if isinstance(self.announcement_bar, mknode.MkNode):
            files |= self.announcement_bar.all_virtual_files()
        return files

    def set_primary_foreground_color(
        self,
        color: datatypes.ColorType,
        light_shade: datatypes.ColorType | None = None,
        dark_shade: datatypes.ColorType | None = None,
    ):
        self.root_css.set_primary_foreground_color(color, light_shade, dark_shade)
        self._foreground_color = color
        self.config.set_color("primary", "custom")

    def set_primary_background_color(self, color: datatypes.RGBColorType):
        self.root_css.set_primary_background_color(color)
        self.config.set_color("primary", "custom")

    def set_accent_foreground_color(self, color: datatypes.RGBColorType):
        self.root_css.set_accent_foreground_color(color)
        self.config.set_color("accent", "custom")

    def get_primary_color(self):
        if self._foreground_color:
            return self._foreground_color
        return self.config.get_primary_color()

    def get_text_color(self):
        return self.config.get_text_color()


if __name__ == "__main__":
    project = Project()
    bs = project.task_runners
    print(bs)

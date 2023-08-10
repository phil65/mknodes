from __future__ import annotations

import logging
import re
import types

from mknodes import mknav
from mknodes.data import commitconventions
from mknodes.utils import helpers, packageinfo


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
        module: types.ModuleType,
        package_managers: list[str] | None = None,
        commit_types: list[commitconventions.CommitTypeStr]
        | commitconventions.ConventionTypeStr
        | None = None,
    ):
        self.module = module
        self.package_name = module.__name__
        self.package_managers = package_managers or ["pip"]
        self.commit_types = commit_types
        self.info = packageinfo.get_info(self.package_name)
        self._root_nav = None

    def get_repository_url(self):
        config = helpers.get_mkdocs_config("mkdocs.yml")
        if config.repo_url:
            return config.repo_url
        return self.info.get_repository_url()

    def get_repository_username(self) -> str | None:
        if match := GITHUB_REGEX.match(self.get_repository_url() or ""):
            return match.group(1)
        return None

    def get_repository_name(self) -> str | None:
        if match := GITHUB_REGEX.match(self.get_repository_url() or ""):
            return match.group(2)
        return None

    def get_root(self, **kwargs):
        if not self._root_nav:
            self._root_nav = mknav.MkNav(project=self, **kwargs)
        return self._root_nav

    def __repr__(self):
        return helpers.get_repr(self, path=self.path)


if __name__ == "__main__":
    import mkdocs

    project = Project(mkdocs)
    bs = project.build_system()
    print(bs)

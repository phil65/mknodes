from __future__ import annotations

import logging
import pathlib
import re
import types

from mknodes import config, mknav
from mknodes.data import commitconventions, installmethods
from mknodes.utils import helpers, packageinfo, pyproject


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
        package_repos: list[installmethods.InstallMethodStr] | None = None,
        commit_types: list[commitconventions.CommitTypeStr]
        | commitconventions.ConventionTypeStr
        | None = None,
    ):
        self.module = module
        self.package_name = module.__name__
        self.package_repos = package_repos or ["pip"]
        self.commit_types = commit_types
        self.pyproject = pyproject.PyProject()
        self.info = packageinfo.get_info(self.package_name)

    def __repr__(self):
        return helpers.get_repr(self, module=self.module)

    def get_repository_url(self) -> str | None:
        if url := config.get_repository_url():
            return url
        return self.info.get_repository_url()

    def get_repository_username(self) -> str | None:
        if match := GITHUB_REGEX.match(self.get_repository_url() or ""):
            return match.group(1)
        return None

    def get_repository_name(self) -> str | None:
        if match := GITHUB_REGEX.match(self.get_repository_url() or ""):
            return match.group(2)
        return None

    def get_root(self, **kwargs) -> mknav.MkNav:
        return mknav.MkNav(project=self, **kwargs)

    def has_precommit(self) -> bool:
        path = pathlib.Path().absolute()
        while not (path / ".pre-commit-config.yaml").exists() and len(path.parts) > 1:
            path = path.parent
        return len(path.parts) > 1

    def has_conda(self) -> bool:
        path = pathlib.Path().absolute()
        while not (path / "meta.yaml").exists() and len(path.parts) > 1:
            path = path.parent
        return len(path.parts) > 1


if __name__ == "__main__":
    import mknodes

    project = Project(mknodes)
    bs = project.has_precommit()
    print(bs)

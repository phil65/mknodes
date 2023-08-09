from __future__ import annotations

import logging
import types

from mknodes import mknav
from mknodes.data import commitconventions
from mknodes.utils import helpers, packageinfo


logger = logging.getLogger(__name__)


class Project:
    """MkNodes Project."""

    def __init__(
        self,
        module: types.ModuleType,
        package_managers: list[str] | None = None,
        commit_scopes: list[commitconventions.ScopeStr]
        | commitconventions.ConventionTypeStr
        | None = None,
    ):
        self.module = module
        self.package_name = module.__name__
        self.package_managers = package_managers or ["pip"]
        self.commit_scopes = commit_scopes
        self.info = packageinfo.PackageInfo(self.package_name)
        self._root_nav = None

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

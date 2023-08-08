from __future__ import annotations

import logging
import types

from mkdocs import config

from mknodes import mknav
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class Project:
    """MkNodes Project."""

    def __init__(self, module: types.ModuleType = "", package_managers=None):
        self.module = module
        self.package_managers = package_managers or ["pip"]
        self._root_nav = None
        self._config = None

    @property
    def config(self):
        if not self._config:
            self._config = config.load_config("mkdocs.yml")
        return self._config

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

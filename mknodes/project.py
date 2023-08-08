from __future__ import annotations

import logging

from mkdocs import config

from mknodes import mknav
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

mkdocs_config = config.load_config("mkdocs.yml")


class Project:
    """Mkdocs Project."""

    def __init__(self):
        self.config = mkdocs_config
        self.root_nav = mknav.MkNav()

    def __repr__(self):
        return helpers.get_repr(self, path=self.path)


if __name__ == "__main__":
    project = Project()

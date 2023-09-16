from __future__ import annotations

from mknodes.basenodes import mklink
from mknodes.navs import mknav
from mknodes.pages import mkpage


class Navigation(dict):
    """An object representing MkDocs navigation."""

    @property
    def navs(self) -> list[mknav.MkNav]:
        """Return all registered navs."""
        return [node for node in self.values() if isinstance(node, mknav.MkNav)]

    @property
    def pages(self) -> list[mkpage.MkPage]:
        """Return all registered pages."""
        return [node for node in self.values() if isinstance(node, mkpage.MkPage)]

    @property
    def links(self) -> list[mklink.MkLink]:
        """Return all registered links."""
        return [node for node in self.values() if isinstance(node, mklink.MkLink)]

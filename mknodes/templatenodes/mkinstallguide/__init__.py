from __future__ import annotations

from typing import Any

from mknodes.templatenodes import mktemplate
from mknodes.data import installmethods
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkInstallGuide(mktemplate.MkTemplate):
    """Node to display an install guide."""

    ICON = "material/help"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        distribution: str | None = None,
        *,
        package_repos: list[installmethods.InstallMethodStr] | None = None,
        header_level: int = 3,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            distribution: name of the distribution to install
            package_repos: package repositories the project is available on
            header_level: Header level for each section
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self._distribution = distribution
        self.header_level = header_level
        self._package_repos = package_repos

    @property
    def package_repos(self) -> list[installmethods.InstallMethod]:
        if self._package_repos:
            return [
                installmethods.InstallMethod.by_id(i)(self.distribution)
                for i in self._package_repos
            ]
        return self.ctx.metadata.package_repos or []

    @property
    def distribution(self):
        return self._distribution or self.ctx.metadata.distribution_name

    @distribution.setter
    def distribution(self, value):
        self._distribution = value


if __name__ == "__main__":
    guide = MkInstallGuide.with_context()
    print(guide)

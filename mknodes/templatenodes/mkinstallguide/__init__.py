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
    def package_repos(self) -> list[installmethods.InstallMethodStr]:
        if self._package_repos:
            return self._package_repos
        return self.ctx.metadata.package_repos or ["pip"]

    @property
    def distribution(self):
        return self._distribution or self.ctx.metadata.distribution_name

    @distribution.setter
    def distribution(self, value):
        self._distribution = value

    @property
    def install_methods(self):
        if not self.distribution:
            return []
        klasses = [installmethods.InstallMethod.by_id(i) for i in self.package_repos]
        return [i(self.distribution) for i in klasses]

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # this will show an install guide for our associated project
        node = MkInstallGuide()
        page += mk.MkReprRawRendered(node, header="### From project")

        # we can also explicitely define the repositories
        node = MkInstallGuide("mkdocs", package_repos=["pipx"])
        page += mk.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    guide = MkInstallGuide.with_context()
    print(guide)

from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mkheader, mknode, mktext
from mknodes.data import installmethods
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkInstallGuide(mkcontainer.MkContainer):
    """Node to display an install guide."""

    ICON = "material/help"

    def __init__(
        self,
        distribution: str | None = None,
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
        super().__init__(**kwargs)
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
    def items(self) -> list[mknode.MkNode]:
        if not self.distribution:
            return []
        klasses = [installmethods.InstallMethod.by_id(i) for i in self.package_repos]
        methods = [i(self.distribution) for i in klasses]
        return [self.get_section_for(method) for method in methods]

    @items.setter
    def items(self, value):
        pass

    def get_section_for(
        self,
        method: installmethods.InstallMethod,
    ) -> mkcontainer.MkContainer:
        items = [
            mkheader.MkHeader(method.ID, level=self.header_level),
            mktext.MkText(method.info_text()),
            mkcode.MkCode(method.install_instructions()),
        ]
        # proj = self.associated_distribution
        # if method.ID == "pip" and proj and (extras := proj.info.extras):
        #     extras_str = ",".join(extras)
        #     text = f"{method.install_instructions()}[{extras_str}]"
        #     code = mkcode.MkCode(text)
        #     items.append(code)
        return mkcontainer.MkContainer(items, parent=self)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            distribution=self._distribution,
            package_repos=self._package_repos,
            header_level=self.header_level,
            _filter_empty=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        # this will show an install guide for our associated project
        node = MkInstallGuide()
        page += mknodes.MkReprRawRendered(node, header="### From project")

        # we can also explicitely define the repositories
        node = MkInstallGuide("mkdocs", package_repos=["pipx"])
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    guide = MkInstallGuide.with_default_context()
    print(guide)

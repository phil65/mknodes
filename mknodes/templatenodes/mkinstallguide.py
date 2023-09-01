from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mkheader, mknode, mktext
from mknodes.data import installmethods
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkInstallGuide(mkcontainer.MkContainer):
    """Node to display an install guide (currently PyPi only)."""

    ICON = "material/help"

    def __init__(
        self,
        project: str | None = None,
        package_repos: list[installmethods.InstallMethodStr] | None = None,
        header_level: int = 3,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            project: name of the project to install
            package_repos: package repositories the project is available on
            header_level: Header level for each section
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._project = project
        self.header_level = header_level
        self._package_repos = package_repos

    @property
    def package_repos(self) -> list[installmethods.InstallMethodStr]:
        if self._package_repos:
            return self._package_repos
        if self.associated_project:
            return self.associated_project.folderinfo.package_repos
        return ["pip"]

    @property
    def project(self):
        if self._project:
            return self._project
        if self.associated_project:
            return self.associated_project.package_name
        return None

    @project.setter
    def project(self, value):
        self._project = value

    @property
    def items(self) -> list[mknode.MkNode]:
        if not self.project:
            return []
        klasses = [installmethods.InstallMethod.by_id(i) for i in self.package_repos]
        methods = [i(self.project) for i in klasses]
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
        # proj = self.associated_project
        # if method.ID == "pip" and proj and (extras := proj.info.extras):
        #     extras_str = ",".join(extras)
        #     text = f"{method.install_instructions()}[{extras_str}]"
        #     code = mkcode.MkCode(text)
        #     items.append(code)
        return mkcontainer.MkContainer(items, parent=self)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            project=self._project,
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
        node = MkInstallGuide(project="mkdocs", package_repos=["pipx"])
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    import mknodes

    project = mknodes.Project.for_mknodes()
    root = project.get_root()
    page = root.add_index_page()
    guide = MkInstallGuide()
    page += guide
    print(page)

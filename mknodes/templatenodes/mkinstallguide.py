from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mkheader, mknode, mktext
from mknodes.data import installmethods
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkInstallGuide(mkcontainer.MkContainer):
    """Install guide text (currently PyPi only)."""

    ICON = "material/help"

    def __init__(
        self,
        project: str | None = None,
        package_managers: list[str] | None = None,
        header_level: int = 3,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            project: name of the project to install
            package_managers: package managers the project can be installed with
            header_level: Header level for each section
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.project = project
        self.header_level = header_level
        self.package_managers = package_managers

    @property
    def items(self) -> list[mknode.MkNode]:
        if self.package_managers:
            managers = self.package_managers
        elif self.associated_project:
            managers = self.associated_project.package_managers
        else:
            managers = ["pip"]
        if self.project:
            project = self.project
        elif self.associated_project:
            project = self.associated_project.package_name
        else:
            msg = "No project set"
            raise ValueError(msg)
        klasses = [installmethods.InstallMethod.by_id(i) for i in managers]
        methods = [i(project) for i in klasses]
        return [self.get_section_for(method) for method in methods]

    @items.setter
    def items(self, value):
        pass

    def get_section_for(
        self,
        method: installmethods.InstallMethod,
    ) -> mkcontainer.MkContainer:
        return mkcontainer.MkContainer(
            [
                mkheader.MkHeader(method.ID, level=self.header_level),
                mktext.MkText(method.info_text()),
                mkcode.MkCode(method.install_instructions()),
            ],
            parent=self,
        )

    def __repr__(self):
        return helpers.get_repr(
            self,
            project=self.project,
            package_managers=self.package_managers,
            header_level=self.header_level,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        # MkInstallGuide is just a text snippet for a short Install guide
        # Currently it is only tailored towards PyPi.

        node = MkInstallGuide(project="mknodes")
        page += mknodes.MkReprRawRendered(node, header="### Default")
        node2 = MkInstallGuide(project="mknodes", package_managers=["pipx"])
        page += mknodes.MkReprRawRendered(node2, header="### Explicit")


if __name__ == "__main__":
    import mknodes

    project = mknodes.Project(mknodes)
    root = project.get_root()
    page = root.add_index_page()
    guide = MkInstallGuide()
    page += guide
    print(page)

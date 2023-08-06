from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mkheader, mknode, mktext
from mknodes.utils import helpers, installmethods


logger = logging.getLogger(__name__)


class MkInstallGuide(mkcontainer.MkContainer):
    """Install guide text (currently PyPi only)."""

    ICON = "material/help"

    def __init__(
        self,
        project: str,
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
        managers = self.package_managers or ["pip"]
        klasses = [installmethods.InstallMethod.by_id(i) for i in managers]
        methods = [i(self.project) for i in klasses]
        return [self.get_section_for(method) for method in methods]

    @items.setter
    def items(self, value):
        pass

    def get_section_for(self, method: installmethods.InstallMethod):
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

        node = MkInstallGuide(project="mknodes", package_managers=["pip", "pipx"])
        page += mknodes.MkReprRawRendered(node, indent=True, header="Pip / Pipx")


if __name__ == "__main__":
    import mknodes

    installguide = MkInstallGuide(project="mknodes")
    print(mknodes.MkReprRawRendered(installguide))

from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mknode, mktext
from mknodes.utils import helpers, installmethods


logger = logging.getLogger(__name__)


class MkInstallGuide(mknode.MkNode):
    """Install guide text (currently PyPi only)."""

    ICON = "material/help"

    def __init__(
        self,
        project: str,
        package_managers: list[str] | None = None,
        header_level: int | None = 3,
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

    def get_nodes(self, install_method):
        return mkcontainer.MkContainer(
            [
                mktext.MkText(install_method.info_text(), parent=self),
                mkcode.MkCode(install_method.install_instructions(), parent=self),
            ],
        )

    def _to_markdown(self) -> str:
        blocks = []
        providers = dict(
            pip=self.get_nodes(installmethods.PipInstall(self.project)),
            pipx=self.get_nodes(installmethods.PipXInstall(self.project)),
            Homebrew=self.get_nodes(installmethods.HomebrewInstall(self.project)),
            Conda=self.get_nodes(installmethods.CondaForgeInstall(self.project)),
        )
        managers = self.package_managers or ["pip"]
        for k, v in providers.items():
            if k in managers:
                if self.header_level:
                    prefix = self.header_level * "#"
                    blocks.append(f"{prefix} {k}\n")
                blocks.append(str(v).format(project=self.project))
        return "\n\n".join(blocks)

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
    installguide = MkInstallGuide(project="mknodes")
    print(installguide)

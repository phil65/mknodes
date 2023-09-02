from __future__ import annotations

import logging

from typing import Literal

from mknodes.basenodes import mktable
from mknodes.info import packageinfo
from mknodes.utils import layouts, reprhelpers


logger = logging.getLogger(__name__)

PackageLayoutStr = Literal["default", "badge"]


class MkDependencyTable(mktable.MkTable):
    """Node for a table showing dependencies for a package."""

    ICON = "material/database"
    STATUS = "new"

    def __init__(
        self,
        package: str | packageinfo.PackageInfo | None = None,
        layout: PackageLayoutStr = "default",
        **kwargs,
    ):
        self._package = package
        match layout:
            case "default":
                self.layouter = layouts.DefaultPackageLayout()
            case "badge":
                self.layouter = layouts.BadgePackageLayout()
            case _:
                raise ValueError(layout)
        super().__init__(**kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, package=self._package, _filter_empty=True)

    @property
    def package(self) -> packageinfo.PackageInfo | None:  # type: ignore[return]
        match self._package:
            case None if self.associated_project:
                return self.associated_project.info
            case str():
                return packageinfo.get_info(self._package)
            case packageinfo.PackageInfo():
                return self._package
            case _:
                return None

    @package.setter
    def package(self, value):
        self._package = value

    @property
    def data(self):
        if not self.package:
            return {}
        packages = self.package.get_required_packages()
        if data := [self.layouter.get_row_for(kls) for kls in packages.items()]:
            return {
                k: [self.to_child_node(dic[k]) for dic in data]  # type: ignore[index]
                for k in data[0]
            }
        return {}

    @staticmethod
    def create_example_page(page):
        import mknodes

        node_1 = MkDependencyTable()
        page += mknodes.MkReprRawRendered(node_1, header="### From project")
        node_2 = MkDependencyTable("mkdocs")
        page += mknodes.MkReprRawRendered(node_2, header="### Explicitely defined")
        node_3 = MkDependencyTable(layout="badge")
        page += mknodes.MkReprRawRendered(node_3, header="### From project")


if __name__ == "__main__":
    table = MkDependencyTable("mknodes")
    logger.warning(table)

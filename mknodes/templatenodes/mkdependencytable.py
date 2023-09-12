from __future__ import annotations

from typing import Literal

from mknodes.basenodes import mktable
from mknodes.info import packageinfo, packageregistry
from mknodes.utils import layouts, log, reprhelpers
from mknodes.utils.packagehelpers import Dependency


logger = log.get_logger(__name__)

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
        self.package = package
        match layout:
            case "default":
                self.layouter = layouts.DefaultPackageLayout()
            case "badge":
                self.layouter = layouts.BadgePackageLayout()
            case _:
                raise ValueError(layout)
        super().__init__(**kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, package=self.package, _filter_empty=True)

    @property
    def required_packages(self) -> dict[packageinfo.PackageInfo, Dependency] | None:
        match self.package:
            case None:
                return self.ctx.metadata.required_packages
            case str():
                return packageregistry.get_info(self.package).required_packages
            case packageinfo.PackageInfo():
                return self.package.required_packages
            case _:
                return None

    @property
    def data(self):
        if not self.required_packages:
            return {}
        packages = self.required_packages
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

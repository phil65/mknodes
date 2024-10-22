from __future__ import annotations

from typing import Any, Literal, TYPE_CHECKING

from mknodes.templatenodes import mktemplatetable
from mknodes.info import packageinfo, packageregistry
from mknodes.utils import log

if TYPE_CHECKING:
    from mknodes.utils.packagehelpers import Dependency


logger = log.get_logger(__name__)

PackageLayoutStr = Literal["default", "badge"]


class MkDependencyTable(mktemplatetable.MkTemplateTable):
    """Node for a table showing dependencies for a package."""

    ICON = "material/database"
    STATUS = "new"

    def __init__(
        self,
        package: str | packageinfo.PackageInfo | None = None,
        *,
        layout: PackageLayoutStr = "default",
        **kwargs: Any,
    ):
        self.package = package
        super().__init__(layout=layout, **kwargs)

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

    def iter_items(self):
        if not self.required_packages:
            return
        yield from [
            dict(package_info=package_info, dep_info=dep_info)
            for (package_info, dep_info) in self.required_packages.items()
        ]


if __name__ == "__main__":
    table = MkDependencyTable("mknodes")
    print(table)

from __future__ import annotations

import logging
import re

from mknodes.basenodes import mklink, mktable
from mknodes.utils import helpers, packageinfo


logger = logging.getLogger(__name__)


class MkDependencyTable(mktable.MkTable):
    """Node for a table showing dependencies for a package."""

    ICON = "material/database"
    STATUS = "new"

    def __init__(self, package: str | packageinfo.PackageInfo | None = None, **kwargs):
        self._package = package
        super().__init__(**kwargs)

    def __repr__(self):
        return helpers.get_repr(self, package=self._package, _filter_empty=True)

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
        rows = []
        for package_info, dep_info in self.package.get_required_packages().items():
            if url := package_info.homepage:
                node = mklink.MkLink(url, package_info.name)
            else:
                node = f"`{package_info.name}`"
            link = helpers.styled(node, size=3, bold=True)
            marker = str(dep_info.marker) if dep_info.marker else ""
            marker_str = re.sub(r'([A-Za-z_]* [>|=|<]* ".*?")', r"`\g<1>`", marker)
            summary = helpers.styled(package_info.metadata["Summary"], italic=True)
            row = dict(Name=link, Summary=summary, Markers=marker_str)
            rows.append(row)
        return {
            k: [self.to_item(dic[k]) for dic in rows]  # type: ignore[index]
            for k in rows[0]
        }

    @staticmethod
    def create_example_page(page):
        import mknodes

        node_1 = MkDependencyTable()
        node_2 = MkDependencyTable("mkdocs")
        page += mknodes.MkReprRawRendered(node_1, header="### From project")
        page += mknodes.MkReprRawRendered(node_2, header="### Explicitely defined")


if __name__ == "__main__":
    table = MkDependencyTable("mknodes")
    logger.warning(table)

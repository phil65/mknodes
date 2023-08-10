from __future__ import annotations

import logging

from mknodes.basenodes import mklink, mktable
from mknodes.utils import helpers, packageinfo


logger = logging.getLogger(__name__)


class MkDependencyTable(mktable.MkTable):
    """Table showing info dependencies for a package."""

    def __init__(self, package: str | packageinfo.PackageInfo | None = None, **kwargs):
        self.package = package
        super().__init__(**kwargs)

    def __repr__(self):
        return helpers.get_repr(self, package=self.package, _filter_empty=True)

    @property
    def data(self):
        match self.package:
            case None if self.associated_project:
                info = self.associated_project.info
            case str():
                info = packageinfo.get_info(self.package)
            case packageinfo.PackageInfo():
                info = self.package
            case _:
                return {}
        rows = []
        for package_info, dep_info in info.get_required_packages().items():
            if url := package_info.get_repository_url():
                node = mklink.MkLink(url, package_info.name)
            else:
                node = f"`{package_info.name}`"
            row = dict(
                Name=node,
                Summary=package_info.metadata["Summary"],
                Markers=str(dep_info.marker) if dep_info.marker else "",
                Website=package_info.get_repository_url(),
            )
            rows.append(row)
        return {
            k: [self.to_item(dic[k]) for dic in rows]  # type: ignore[index]
            for k in rows[0]
        }

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        node_1 = MkDependencyTable()
        node_2 = MkDependencyTable("mkdocs")
        page += mknodes.MkReprRawRendered(node_1, header="### From project")
        page += mknodes.MkReprRawRendered(node_2, header="### Explicitely defined")


if __name__ == "__main__":
    table = MkDependencyTable("mknodes")
    logger.warning(table)

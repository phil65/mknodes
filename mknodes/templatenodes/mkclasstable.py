from __future__ import annotations

import logging

from typing import Literal

from mknodes.basenodes import mktable
from mknodes.utils import layouts, linkprovider, reprhelpers


logger = logging.getLogger(__name__)


class MkClassTable(mktable.MkTable):
    """Node for a table showing info for a list of classes."""

    def __init__(
        self,
        klasses: list[type] | set[type],
        *,
        layout: Literal["compact", "extended"] | layouts.Layout = "extended",
        **kwargs,
    ):
        self.klasses = klasses
        # STRIP_CODE = r"```[^\S\r\n]*[a-z]*\n.*?\n```"
        # docs = [re.sub(STRIP_CODE, '', k.__module__, 0, re.DOTALL) for k in klasses]
        self.layout = layout
        super().__init__(**kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, layout=self.layout, klasses=self.klasses)

    @property
    def linkprovider(self):
        if self.associated_project:
            return self.associated_project.linkprovider
        return linkprovider.LinkProvider()

    @property
    def layouter(self):
        match self.layout:
            case "compact":
                return layouts.CompactClassLayout(link_provider=self.linkprovider)
            case "extended":
                return layouts.ExtendedClassLayout(link_provider=self.linkprovider)
            case layouts.Layout():
                return self.layout
            case _:
                raise ValueError(self.layout)

    @property
    def data(self):
        if not self.klasses:
            return {}
        data = [self.layouter.get_row_for(kls) for kls in self.klasses]
        return {
            k: [self.to_child_node(dic[k]) for dic in data]  # type: ignore[index]
            for k in data[0]
        }

    @staticmethod
    def create_example_page(page):
        import mknodes

        node_1 = MkClassTable(
            klasses=[mknodes.MkTable, MkClassTable, mknodes.MkNav],
            layout="compact",
        )
        node_2 = MkClassTable(
            klasses=[mknodes.MkTable, MkClassTable, mknodes.MkNav],
            layout="extended",
        )
        page += mknodes.MkReprRawRendered(node_1, header="### Compact layout")
        page += mknodes.MkReprRawRendered(node_2, header="### Extended layout")


if __name__ == "__main__":
    table = MkClassTable(klasses=[mktable.MkTable], layout="extended")
    print(table)

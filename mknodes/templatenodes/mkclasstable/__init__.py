from __future__ import annotations

from mknodes.info import grifferegistry
from mknodes.templatenodes import mktemplatetable
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkClassTable(mktemplatetable.MkTemplateTable):
    """Node for a table showing info for a list of classes."""

    def __init__(
        self,
        klasses: list[type] | set[type],
        *,
        layout: str = "default",
        **kwargs,
    ):
        self.klasses = klasses
        super().__init__(layout=layout, **kwargs)

    def iter_items(self):
        yield from [
            dict(kls=kls, griffe_kls=grifferegistry.get_class(kls))
            for kls in self.klasses
        ]

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        klasses = [mk.MkTable, MkClassTable, mk.MkNav]
        node_1 = MkClassTable(klasses=klasses, layout="compact")
        node_2 = MkClassTable(klasses=klasses, layout="default")
        page += mk.MkReprRawRendered(node_1, header="### Compact layout")
        page += mk.MkReprRawRendered(node_2, header="### Extended layout")


if __name__ == "__main__":
    table = MkClassTable(klasses=[mktemplatetable.MkTemplateTable], layout="default")
    print(table)

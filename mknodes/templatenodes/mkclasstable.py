from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Literal

from mknodes.basenodes import mktable
from mknodes.utils import helpers, layouts


logger = logging.getLogger(__name__)


class MkClassTable(mktable.MkTable):
    """Node for a table showing info for a list of classes."""

    def __init__(
        self,
        klasses: list[type] | set[type],
        *,
        layout: Literal["compact", "extended"] = "extended",
        filter_fn: Callable | None = None,
        **kwargs,
    ):
        self.klasses = klasses
        # STRIP_CODE = r"```[^\S\r\n]*[a-z]*\n.*?\n```"
        # docs = [re.sub(STRIP_CODE, '', k.__module__, 0, re.DOTALL) for k in klasses]
        match layout:
            case "compact":
                self.layouter = layouts.CompactClassLayout()
            case "extended":
                self.layouter = layouts.ExtendedClassLayout(subclass_predicate=filter_fn)
            case _:
                raise ValueError(layout)
        super().__init__(**kwargs)

    def __repr__(self):
        return helpers.get_repr(self, klasses=self.klasses)

    @property
    def data(self):
        if not self.klasses:
            return {}
        data = [self.layouter.get_row_for(kls) for kls in self.klasses]
        return {
            k: [self.to_item(dic[k]) for dic in data]  # type: ignore[index]
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

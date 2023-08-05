from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Literal

from mknodes.basenodes import mktable
from mknodes.utils import helpers, layouts


logger = logging.getLogger(__name__)


class MkClassTable(mktable.MkTable):
    """Table showing info for a list of classes."""

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
                layouter = layouts.CompactClassLayout()
            case "extended":
                layouter = layouts.ExtendedClassLayout(subclass_predicate=filter_fn)
            case _:
                raise ValueError(layout)

        data = [layouter.get_row_for(kls) for kls in klasses]
        super().__init__(data=data, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, klasses=self.klasses)

    @staticmethod
    def create_example_page(page):
        import mknodes

        node_1 = MkClassTable(
            klasses=[mknodes.MkTable, MkClassTable, mknodes.MkNav],
            layout="compact",
            header="Compact layout",
        )
        node_2 = MkClassTable(
            klasses=[mknodes.MkTable, MkClassTable, mknodes.MkNav],
            layout="extended",
            header="Extended layout",
        )
        page += mknodes.MkReprRawRendered(node_1)
        page += mknodes.MkReprRawRendered(node_2)


if __name__ == "__main__":
    table = MkClassTable(klasses=[mktable.MkTable], layout="extended")
    print(table)

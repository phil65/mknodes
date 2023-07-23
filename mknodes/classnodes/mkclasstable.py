from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Literal

from mknodes.classnodes import mkbaseclasstable
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkClassTable(mkbaseclasstable.MkBaseClassTable):
    """Table to show information about a specific class."""

    def __init__(
        self,
        klass: type,
        *,
        layout: Literal["compact", "extended"] = "extended",
        filter_fn: Callable | None = None,
        mode: Literal["sub_classes", "parent_classes"] = "sub_classes",
        **kwargs,
    ):
        self.mode = mode
        self.klass = klass
        match self.mode:
            case "sub_classes":
                try:
                    klasses = klass.__subclasses__()
                except TypeError:
                    klasses = []
            case "parent_classes":
                klasses = list(klass.__bases__)
            case _:
                raise ValueError(self.mode)
        super().__init__(klasses=klasses, layout=layout, filter_fn=filter_fn, **kwargs)

    def __repr__(self):
        return helpers.get_repr(
            self,
            klass=self.klass,
            mode=self.mode,
        )

    @staticmethod
    def examples():
        from mknodes import mknav

        yield dict(klass=mknav.MkNav)
        yield dict(klass=mknav.MkNav, mode="parent_classes")


if __name__ == "__main__":
    table = MkClassTable(klass=MkClassTable, layout="extended")
    print(table)

from __future__ import annotations

import logging

from typing import Literal

from markdownizer import baseclasstable, utils


logger = logging.getLogger(__name__)


class ClassTable(baseclasstable.BaseClassTable):
    """Table to show information about a specific class."""

    def __init__(
        self,
        klass: type,
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
                klasses = klass.__bases__
            case _:
                raise ValueError(self.mode)
        super().__init__(klasses=klasses, **kwargs)

    def __repr__(self):
        return utils.get_repr(
            self,
            klass=self.klass,
            mode=self.mode,
        )

    @staticmethod
    def examples():
        from markdownizer import nav

        yield dict(klass=nav.Nav)
        yield dict(klass=nav.Nav, mode="parent_classes")


if __name__ == "__main__":
    table = ClassTable(klass=ClassTable, layout="extended")
    print(table)

from __future__ import annotations

import griffe

from mknodes.info import grifferegistry
from mknodes.templatenodes import mktemplatetable
from mknodes.utils import classhelpers, log
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = log.get_logger(__name__)


class MkClassTable(mktemplatetable.MkTemplateTable):
    """Node for a table showing info for a list of classes."""

    def __init__(
        self,
        klasses: Sequence[type | str | griffe.Class],
        *,
        layout: str = "default",
        **kwargs,
    ):
        self.klasses = klasses
        super().__init__(layout=layout, **kwargs)

    def iter_items(self):
        for kls in self.klasses:
            match kls:
                case type():
                    yield dict(kls=kls, griffe_kls=grifferegistry.get_class(kls))
                case griffe.Class():
                    yield dict(kls=classhelpers.import_module(kls.path), griffe_kls=kls)
                case str():
                    yield dict(
                        kls=classhelpers.import_module(kls),
                        griffe_kls=grifferegistry.get_class(kls),
                    )


if __name__ == "__main__":
    table = MkClassTable(klasses=[mktemplatetable.MkTemplateTable], layout="default")
    print(table)

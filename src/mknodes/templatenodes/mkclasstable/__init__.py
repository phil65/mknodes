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
    ) -> None:
        self.klasses = klasses
        super().__init__(layout=layout, **kwargs)

    def iter_items(self):
        for kls in self.klasses:
            match kls:
                case type():
                    yield dict(kls=kls, griffe_kls=_get_griffe_class(kls))
                case griffe.Class():
                    yield dict(kls=classhelpers.import_module(kls.path), griffe_kls=kls)
                case str():
                    yield dict(
                        kls=classhelpers.import_module(kls),
                        griffe_kls=_get_griffe_class(kls),
                    )


def _get_griffe_class(kls: type | str) -> griffe.Class | griffe.Alias | None:
    """Griffe info for a table row, or None if griffe doesn't know the class.

    griffe's `builtins` has no `type` / `object`, so e.g. the base class table of a
    metaclass would fail. The built-in layouts only need the class itself.
    """
    try:
        return grifferegistry.get_class(kls)
    except KeyError:
        logger.debug("No griffe info for %r", kls)
        return None


if __name__ == "__main__":
    table = MkClassTable(klasses=[mktemplatetable.MkTemplateTable], layout="default")
    print(table)

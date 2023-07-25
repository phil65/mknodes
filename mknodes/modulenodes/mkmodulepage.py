from __future__ import annotations

import logging
import os
import pathlib
import types

from mknodes import mkdocstrings, mkpage
from mknodes.classnodes import mkclasstable
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkModulePage(mkpage.MkPage):
    """Page showing information about a module.

    Arguments:
        module: ModuleType or path to model to show info for.
        path: Some path for the file. Default is index.md
        docstrings: Whether to show docstrings for given module.
        show_class_table: ModuleType or path to model to show info for.
    """

    def __init__(
        self,
        module: tuple[str, ...] | str | types.ModuleType,
        *,
        klasses: list[type] | set[type] | None = None,
        path: str | os.PathLike = "index.md",
        docstrings: bool = False,
        show_class_table: bool = True,
        **kwargs,
    ):
        path = pathlib.Path(path)
        super().__init__(path=path, **kwargs)
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(module)
        self.docstrings = docstrings
        self.klasses = klasses or list(
            classhelpers.iter_classes(module=self.parts, module_filter=self.parts[0]),
        )
        self.show_class_table = show_class_table
        self._build()

    def __repr__(self):
        return helpers.get_repr(self, module=self.module, path=str(self.path))

    @staticmethod
    def examples():
        import mknodes

        yield dict(module=mknodes)

    def _build(self):
        if doc := self.module.__doc__:
            self.append(doc)
        if self.docstrings:
            item = mkdocstrings.MkDocStrings(f'{".".join(self.parts)}')
            self.append(item)
        if self.show_class_table:
            table = mkclasstable.MkClassTable(self.klasses)
            self.append(table)


if __name__ == "__main__":
    doc = MkModulePage(mkpage)
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

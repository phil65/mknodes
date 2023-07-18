from __future__ import annotations

import logging
import os
import pathlib
import types

from mknodes import baseclasstable, classhelpers, docstrings, mkpage, utils


logger = logging.getLogger(__name__)


class ModulePage(mkpage.MkPage):
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
        path: str | os.PathLike = "index.md",
        docstrings: bool = False,
        show_class_table: bool = True,
        **kwargs,
    ):
        path = pathlib.Path(path)
        super().__init__(path=path, **kwargs)
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(self.parts)
        self.docstrings = docstrings
        self.show_class_table = show_class_table
        self._build()

    def __repr__(self):
        return utils.get_repr(self, module=self.module, path=str(self.path))

    @staticmethod
    def examples():
        import mknodes

        yield dict(module=mknodes)

    def _build(self):
        if doc := self.module.__doc__:
            self.append(doc)
        if self.docstrings:
            self.append(docstrings.DocStrings(f'{".".join(self.parts)}'))
        if self.show_class_table:
            klasses = list(
                classhelpers.iter_classes_for_module(
                    self.parts, module_filter=self.parts[0]
                )
            )
            self.append(baseclasstable.BaseClassTable(klasses))


if __name__ == "__main__":
    doc = ModulePage(mkpage)
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

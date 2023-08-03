from __future__ import annotations

import logging
import os
import types

from typing import Any

from mknodes.pages import mktemplatepage, processors
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkModulePage(mktemplatepage.MkTemplatePage):
    """Page showing information about a module."""

    def __init__(
        self,
        module: tuple[str, ...] | str | types.ModuleType,
        *,
        klasses: list[type] | set[type] | None = None,
        path: str | os.PathLike = "index.md",
        docstrings: bool = False,
        show_class_table: bool = True,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: ModuleType or path to model to show info for.
            path: Some path for the file. Default is index.md
            klasses: klasses to use
            docstrings: Whether to show docstrings for given module.
            show_class_table: ModuleType or path to model to show info for.
            kwargs: further keyword arguments passed to parent
        """
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(module)
        self.docstrings = docstrings
        self.klasses = klasses or list(
            classhelpers.iter_classes(module=self.parts, module_filter=self.parts[0]),
        )
        self.show_class_table = show_class_table
        super().__init__(path=path, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, module=self.module, path=str(self.path))

    def get_processors(self) -> list:
        procs: list[processors.PageProcessor] = [processors.DocPageProcessor(self.module)]
        if self.show_class_table:
            proc = processors.ClassTablePageProcessor(self.klasses)
            procs.append(proc)
        if self.docstrings:
            proc = processors.MkDocStringPageProcessor(self.module)
            procs.append(proc)
        return procs


if __name__ == "__main__":
    doc = MkModulePage(mktemplatepage)
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

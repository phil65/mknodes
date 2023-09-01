from __future__ import annotations

import logging
import os
import types

from typing import Any

from mknodes.pages import mktemplatepage, processors
from mknodes.utils import classhelpers, reprhelpers


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
        show_module_table: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: ModuleType or path to model to show info for.
            path: Some path for the file. Default is index.md
            klasses: klasses to use
            docstrings: Whether to show docstrings for given module.
            show_class_table: Whether to show a table with classes part of the module
            show_module_table: Whether to show a table with submodules
            kwargs: further keyword arguments passed to parent
        """
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(module)
        self.docstrings = docstrings
        self.klasses = klasses or list(
            classhelpers.iter_classes(module=self.parts, module_filter=self.parts[0]),
        )
        self.show_class_table = show_class_table
        self.show_module_table = show_module_table
        super().__init__(path=path, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, module=self.module, path=str(self.path))

    def get_pageprocessors(self) -> list:
        procs: list[processors.ContainerProcessor] = [
            processors.DocContainerProcessor(self.module),
        ]
        if self.show_class_table:
            proc = processors.ClassTableContainerProcessor(self.klasses)
            procs.append(proc)
        if self.show_module_table:
            proc = processors.ModuleTableContainerProcessor(self.module)
            procs.append(proc)
        if self.docstrings:
            proc = processors.MkDocStringContainerProcessor(self.module)
            procs.append(proc)
        return procs


if __name__ == "__main__":
    doc = MkModulePage(mktemplatepage)
    print(doc)

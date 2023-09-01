from __future__ import annotations

import logging
import os
import pathlib

from typing import Any

from mknodes.pages import mktemplatepage, processors
from mknodes.utils import classhelpers, reprhelpers


logger = logging.getLogger(__name__)


class MkClassPage(mktemplatepage.MkTemplatePage):
    """Page showing information about a class."""

    def __init__(
        self,
        klass: type,
        *,
        module_path: tuple[str, ...] | str | None = None,
        path: str | os.PathLike = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            klass: class to show info for
            module_path: If given, overrides module returned by class.__module__
                         This can be useful if you want to link to an aliased class
                         (for example a class imported to __init__.py)
            path: some path for the file.
            kwargs: keyword arguments passed to base class
        """
        # TODO: should path be settable?
        path = pathlib.Path(f"{klass.__name__}.md")
        self.klass = klass
        match module_path:
            case None:
                self.parts = klass.__module__.split(".")
            case _:
                self.parts = classhelpers.to_module_parts(module_path)
        super().__init__(path=path, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, klass=self.klass, path=str(self.path))

    def get_pageprocessors(self):
        return [
            processors.BaseClassTableContainerProcessor(self.klass),
            processors.SubClassTableContainerProcessor(self.klass),
            processors.InheritanceDiagramContainerProcessor(self.klass),
            processors.MkDocStringContainerProcessor(self.klass),
        ]


if __name__ == "__main__":
    doc = MkClassPage(MkClassPage)
    print(doc)

from __future__ import annotations

import logging
import os
import pathlib

from typing import Any

from mknodes import mkpage
from mknodes.templatenodes import processors
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkClassPage(mkpage.MkPage):
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
        super().__init__(path=path, **kwargs)
        self.klass = klass
        match module_path:
            case None:
                self.parts = klass.__module__.split(".")
            case _:
                self.parts = classhelpers.to_module_parts(module_path)
        self._build()

    def __repr__(self):
        return helpers.get_repr(self, klass=self.klass, path=str(self.path))

    @staticmethod
    def create_example_page(page):
        import mknodes

        # MkClassPages are page templates to display
        # documentation about a class.
        node = MkClassPage(klass=mknodes.MkText)
        page += mknodes.MkReprRawRendered(node)

    def get_processors(self):
        return [
            processors.BaseClassTablePageProcessor(self.klass),
            processors.SubClassTablePageProcessor(self.klass),
            processors.InheritanceDiagramPageProcessor(self.klass),
            processors.MkDocStringPageProcessor(self.klass),
        ]

    def _build(self):
        for processor in self.get_processors():
            if processor.check_if_apply(self):
                processor.append_section(self)


if __name__ == "__main__":
    doc = MkClassPage(MkClassPage)
    doc.add_admonition("Warning. This is still beta", typ="danger", title="Warning")
    print(doc)
    # print(doc.children)

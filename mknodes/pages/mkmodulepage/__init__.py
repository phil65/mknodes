from __future__ import annotations

import os
import types

from typing import Any

from mknodes.info import grifferegistry
from mknodes.pages import mktemplatepage
from mknodes.utils import classhelpers, log, reprhelpers


DEFAULT_TPL = "modulepage.md"

logger = log.get_logger(__name__)


class MkModulePage(mktemplatepage.MkTemplatePage):
    """Page showing information about a module."""

    def __init__(
        self,
        module: tuple[str, ...] | str | types.ModuleType,
        *,
        klasses: list[type] | set[type] | None = None,
        path: str | os.PathLike | None = None,
        template: str | os.PathLike | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: ModuleType or path to model to show info for.
            klasses: klasses to use
            path: Filename/path for the Module page. defaults to [modulename].md
            template: Name of the template to load
            kwargs: further keyword arguments passed to parent
        """
        self.parts = classhelpers.to_module_parts(module)
        self.module = classhelpers.to_module(module)
        self.klasses = klasses or list(
            classhelpers.iter_classes(module=self.parts, module_filter=self.parts[0]),
        )
        tpl_name = template or DEFAULT_TPL
        super().__init__(
            template=tpl_name,
            template_parent=DEFAULT_TPL if tpl_name != DEFAULT_TPL else None,
            path=path or f"{self.parts[-1]}.md",
            **kwargs,
        )

    def __repr__(self):
        return reprhelpers.get_repr(self, module=self.module, path=self.path)

    @property
    def extra_variables(self) -> dict[str, Any]:
        variables: dict[str, Any] = dict(module=self.module, klasses=self.klasses)
        variables["griffe_obj"] = grifferegistry.get_module(self.module)
        return variables


if __name__ == "__main__":
    doc = MkModulePage(mktemplatepage)
    print(doc)

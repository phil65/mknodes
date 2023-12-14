from __future__ import annotations


import pathlib
from typing import Any, TYPE_CHECKING

from mknodes.info import grifferegistry
from mknodes.pages import mktemplatepage
from mknodes.utils import classhelpers, inspecthelpers, log, reprhelpers

if TYPE_CHECKING:
    import types


logger = log.get_logger(__name__)


class MkModulePage(mktemplatepage.MkTemplatePage):
    """Page showing information about a module."""

    DEFAULT_TPL = "modulepage.md"

    def __init__(
        self,
        module: tuple[str, ...] | str | types.ModuleType,
        *,
        klasses: list[type] | set[type] | None = None,
        title: str | None = None,
        template_path: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            module: ModuleType or path to model to show info for.
            klasses: klasses to use
            title: Optional title override. Defaults to module name
            template_path: Name of the template to load
            kwargs: further keyword arguments passed to parent
        """
        self.module = classhelpers.to_module(module)
        self.parts = tuple(self.module.__name__.split("."))
        self.klasses = klasses or classhelpers.list_classes(
            module,
            module_filter=self.parts[0],
        )
        tpl_name = template_path or self.DEFAULT_TPL
        super().__init__(template_path=tpl_name, title=title or self.parts[-1], **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, module=self.module, path=self.path)

    @property
    def extra_variables(self) -> dict[str, Any]:
        griffe_obj = grifferegistry.get_module(self.module)
        variables = dict(module=self.module, klasses=self.klasses, griffe_obj=griffe_obj)
        path = inspecthelpers.get_file(self.module)
        url = self.ctx.metadata.repository_url
        repo_path = self.ctx.metadata.repository_path
        if path and path.is_relative_to(repo_path):
            rel_path = pathlib.Path(path).relative_to(repo_path).as_posix()
            variables["github_url"] = f"{url}blob/main/{rel_path}"
        else:
            variables["github_url"] = None
        return variables


if __name__ == "__main__":
    doc = MkModulePage(mktemplatepage)
    print(doc)

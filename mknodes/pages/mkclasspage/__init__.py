from __future__ import annotations

import pathlib

from typing import Any

from jinjarope import inspectfilters

from mknodes.info import grifferegistry
from mknodes.pages import mktemplatepage
from mknodes.utils import inspecthelpers, log, reprhelpers


logger = log.get_logger(__name__)


class MkClassPage(mktemplatepage.MkTemplatePage):
    """Page showing information about a class."""

    DEFAULT_TPL = "classpage.md"

    def __init__(
        self,
        klass: type,
        *,
        title: str | None = None,
        module_path: tuple[str, ...] | str | None = None,
        template_path: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            klass: class to show info for
            title: Optional title override. Defaults to class name
            module_path: If given, overrides module returned by class.__module__
                         This can be useful if you want to link to an aliased class
                         (for example a class imported to __init__.py)
            template_path: Name of the template to load
            kwargs: keyword arguments passed to base class
        """
        self.klass = klass
        self.module_path = module_path
        # if user chooses custom template, we make default the parent
        tpl = template_path or self.DEFAULT_TPL
        super().__init__(title=title or klass.__name__, template_path=tpl, **kwargs)

    def __repr__(self):
        return reprhelpers.get_nondefault_repr(self)

    @property
    def extra_variables(self) -> dict[str, Any]:
        # right now, we inject the cls and the griffe Class into jinja namespace.
        subclasses = inspectfilters.list_subclasses(self.klass, recursive=False)
        griffe_obj = grifferegistry.registry.get_class(self.klass)
        variables = dict(cls=self.klass, subclasses=subclasses, griffe_obj=griffe_obj)
        p = inspecthelpers.get_file(self.klass)
        repo_path = self.ctx.metadata.repository_path
        if p and p.is_relative_to(repo_path):
            rel_path = pathlib.Path(p).relative_to(repo_path).as_posix()
            klass_url = f"{self.ctx.metadata.repository_url}blob/main/{rel_path}"
            variables["github_url"] = klass_url
        else:
            variables["github_url"] = None
        return variables


if __name__ == "__main__":
    import mknodes as mk

    doc = MkClassPage(mk.MkPluginFlow, template_path="classpage_custom.jinja")
    print(doc.get_resources())

from __future__ import annotations

import os

from typing import Any

from mknodes.info import grifferegistry
from mknodes.pages import mktemplatepage
from mknodes.utils import classhelpers, inspecthelpers, log, reprhelpers


logger = log.get_logger(__name__)


DEFAULT_TPL = "classpage.md"


class MkClassPage(mktemplatepage.MkTemplatePage):
    """Page showing information about a class."""

    def __init__(
        self,
        klass: type,
        *,
        title: str | None = None,
        module_path: tuple[str, ...] | str | None = None,
        template: str | os.PathLike | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            klass: class to show info for
            title: Optional title override. Defaults to class name
            module_path: If given, overrides module returned by class.__module__
                         This can be useful if you want to link to an aliased class
                         (for example a class imported to __init__.py)
            template: Name of the template to load
            kwargs: keyword arguments passed to base class
        """
        self.klass = klass
        self.module_path = module_path
        # if user chooses custom template, we make default the parent
        tpl = template or DEFAULT_TPL
        tpl_parent = DEFAULT_TPL if tpl != DEFAULT_TPL else None
        super().__init__(
            title=title or klass.__name__,
            template=tpl,
            template_parent=tpl_parent,
            **kwargs,
        )

    def __repr__(self):
        return reprhelpers.get_nondefault_repr(self)

    @property
    def extra_variables(self) -> dict[str, Any]:
        # right now, we inject the cls and the griffe Class into jinja namespace.
        subclasses = classhelpers.list_subclasses(self.klass, recursive=False)
        variables = dict(cls=self.klass, subclasses=subclasses)
        mod = self.klass.__module__.replace(".", "/")
        p = inspecthelpers.get_file(self.klass).as_posix()  # type: ignore[union-attr]
        klass_url = f"{self.ctx.metadata.repository_url}blob/main/{p[p.rfind(mod):]}"
        variables["github_url"] = klass_url
        variables["griffe_obj"] = grifferegistry.registry.get_class(self.klass)
        return variables


if __name__ == "__main__":
    import mknodes as mk

    doc = MkClassPage.with_context(mk.MkMaterialBadge, template="classpage_custom.jinja")
    print(doc.get_resources())

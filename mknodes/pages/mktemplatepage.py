from __future__ import annotations

import abc

from mknodes.pages import mkpage
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkTemplatePage(mkpage.MkPage, metaclass=abc.ABCMeta):
    """Abstact Page used for templates."""

    def __init__(
        self,
        *args,
        template_name: str,
        template_parent: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.template_name = template_name
        self.template_parent = template_parent

    @property
    def extra_variables(self):
        return {}

    def to_markdown(self) -> str:
        with self._env.with_globals(**self.extra_variables):
            return self.env.render_template(
                self.template_name,
                parent_template=self.template_parent,
            )

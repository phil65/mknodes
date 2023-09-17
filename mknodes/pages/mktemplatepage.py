from __future__ import annotations

import abc
import os

from mknodes.pages import mkpage
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkTemplatePage(mkpage.MkPage, metaclass=abc.ABCMeta):
    """Abstact Page used for templates."""

    def __init__(
        self,
        *args,
        template: str | os.PathLike,
        template_parent: str | None = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.template_main = template
        self.template_parent = template_parent

    @property
    def extra_variables(self):
        return {}

    def to_markdown(self) -> str:
        with self._env.with_globals(**self.extra_variables):
            if isinstance(self.template_main, os.PathLike):
                return self.env.render_file(
                    self.template_main,
                    parent_template=self.template_parent,
                )
            return self.env.render_template(
                self.template_main,
                parent_template=self.template_parent,
            )

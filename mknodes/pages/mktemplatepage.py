from __future__ import annotations

import abc
import os

from typing import Any

from mknodes.pages import mkpage
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkTemplatePage(mkpage.MkPage, metaclass=abc.ABCMeta):
    """MkPage subclass used for rendering templates."""

    def __init__(
        self,
        *args: Any,
        template: str | os.PathLike,
        template_parent: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            args: Arguments passed to parent
            template: Template to use. Can either be a template path or a PathLike object
                      which will be used as a template.
            template_parent: Optional parent template to use
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(*args, **kwargs)
        self.template_main = template
        self.template_parent = template_parent

    @property
    def children(self):
        self.to_markdown()
        return self.env.rendered_children

    @children.setter
    def children(self, val):
        pass

    @property
    def extra_variables(self) -> dict[str, Any]:
        """Extra variables for the environment. Can be overridden by subclasses."""
        return {}

    def to_markdown(self) -> str:
        with self.env.with_globals(**self.extra_variables):
            if isinstance(self.template_main, os.PathLike):
                return self.env.render_file(self.template_main)
            return self.env.render_template(
                self.template_main,
                parent_template=self.template_parent,
            )

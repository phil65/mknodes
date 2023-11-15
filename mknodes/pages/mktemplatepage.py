from __future__ import annotations

from typing import Any

from mknodes.pages import mkpage
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkTemplatePage(mkpage.MkPage):
    """MkPage subclass used for rendering templates."""

    def __init__(
        self,
        *args: Any,
        template_path: str,
        template_parent: str | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            args: Arguments passed to parent
            template_path: Template to use. Can either be a template path or a PathLike
                           object which will be used as a template.
            template_parent: Optional parent template to use
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(*args, **kwargs)
        self.template_path = template_path
        self.template_parent = template_parent

    @property
    def items(self):
        self._to_markdown()
        return self.env.rendered_children

    @items.setter
    def items(self, val):
        pass

    @property
    def extra_variables(self) -> dict[str, Any]:
        """Extra variables for the environment. Can be overridden by subclasses."""
        return {}

    def _to_markdown(self) -> str:
        return self.env.render_template(
            self.template_path,
            parent_template=self.template_parent,
            variables=self.extra_variables,
        )

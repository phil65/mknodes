from __future__ import annotations

from typing import Any

from mknodes.pages import mkpage
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTemplatePage(mkpage.MkPage):
    """MkPage subclass used for rendering templates."""

    def __init__(
        self,
        *args: Any,
        template_path: str,
        template_parent: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            args: Arguments passed to parent
            template_path: Template to use. Can either be a template path or a PathLike
                           object which will be used as a template.
            template_parent: Optional parent template to use
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(*args, **kwargs)
        self.template_path = template_path
        self.template_parent = template_parent

    def get_items(self):
        self.env.render_template(
            self.template_path,
            parent_template=self.template_parent,
            variables=self.extra_variables,
        )
        return self.env.rendered_children

    @property
    def extra_variables(self) -> dict[str, Any]:
        """Extra variables for the environment. Can be overridden by subclasses."""
        return {}

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: render template once, return both markdown and resources."""
        # Render template once
        md = await self.env.render_template_async(
            self.template_path,
            parent_template=self.template_parent,
            variables=self.extra_variables,
        )

        # Collect resources from rendered children (already created by render above)
        aggregated = await self._build_node_resources()
        for child in self.env.rendered_children:
            child_content = await child.get_content()
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown

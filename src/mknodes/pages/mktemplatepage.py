from typing import Any

from mknodes.jinja.rendercache import TemplateRenderMixin
from mknodes.pages import mkpage
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTemplatePage(TemplateRenderMixin, mkpage.MkPage):
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

    def render_kwargs(self) -> dict[str, Any]:
        return dict(
            template_name=self.template_path,
            parent_template=self.template_parent,
            variables=self.extra_variables,
        )

    def get_items(self):
        return self.get_render_result().children

    @property
    def extra_variables(self) -> dict[str, Any]:
        """Extra variables for the environment. Can be overridden by subclasses."""
        return {}

    def get_content(self) -> resources.NodeContent:
        """Render the template once: Markdown + resources of the created nodes."""
        result = self.current_render_result()
        aggregated = self._build_node_resources()
        for child in result.children:
            aggregated.merge(result.get_resources(child))
        return resources.NodeContent(markdown=result.markdown, resources=aggregated)

    def to_md_unprocessed(self) -> str:
        content = self.get_content()
        return content.markdown

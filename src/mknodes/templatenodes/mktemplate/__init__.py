from typing import Any

from mknodes.basenodes import mkcontainer
from mknodes.jinja.rendercache import TemplateRenderMixin
from mknodes.pages import metadata
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTemplate(TemplateRenderMixin, mkcontainer.MkContainer):
    """Node representing a jinja template.

    Renders templates with the context-aware MkNodes jinja environment.
    Rendered nodes become virtual children of this node.
    Additional variables can be passed to the render process.
    """

    ICON = "simple/jinja"
    STATUS = "new"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        template: str,
        *,
        block: str | None = None,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            template: Jinja template name.
            block: Name of a specific block of the template which should get rendered
            variables: Variables to use for rendering
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.template = template
        self.block = block
        self.variables = variables or {}

    def render_kwargs(self) -> dict[str, Any]:
        return dict(template_name=self.template, variables=self.variables, block_name=self.block)

    def get_items(self):
        return self.get_render_result().children

    def get_content(self) -> resources.NodeContent:
        """Render the template once: Markdown + resources of the created nodes."""
        result = self.current_render_result()
        # Strip YAML frontmatter if present
        _, md = metadata.Metadata.parse(result.markdown)
        aggregated = self._build_node_resources()
        for child in result.children:
            aggregated.merge(result.get_resources(child))
        return resources.NodeContent(markdown=md, resources=aggregated)

    def to_md_unprocessed(self) -> str:
        content = self.get_content()
        return content.markdown


if __name__ == "__main__":

    def main() -> None:
        print(MkTemplate("nodes_index.jinja").get_resources())

    main()

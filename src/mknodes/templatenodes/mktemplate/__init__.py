from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcontainer
from mknodes.pages import metadata
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTemplate(mkcontainer.MkContainer):
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

    def get_items(self):
        self.env.render_template(self.template, variables=self.variables, block_name=self.block)
        return self.env.rendered_children

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: render template once, return both markdown and resources."""
        # Render template once
        result = await self.env.render_template_async(
            self.template,
            variables=self.variables,
            block_name=self.block,
        )
        # Strip YAML frontmatter if present
        _, md = metadata.Metadata.parse(result)
        # Collect resources from rendered children (already created by render above)
        aggregated = await self._build_node_resources()
        for child in self.env.rendered_children:
            child_content = await child.get_content()
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


if __name__ == "__main__":

    async def main() -> None:
        print(await MkTemplate("nodes_index.jinja").get_resources())

    import asyncio

    asyncio.run(main())

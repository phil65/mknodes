from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkJinjaTemplate(mknode.MkNode):
    """Node representing a jinja template."""

    ICON = "simple/jinja"
    STATUS = "new"

    def __init__(
        self,
        template: str,
        *,
        variables: dict | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            template: Jinja template name.
            variables: Variables to use for rendering
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.template = template
        self.variables = variables or {}

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            template=self.template,
            variables=self.variables,
            _filter_empty=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkJinjaTemplate(template="requirements.md")
        page += mknodes.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        return self.env.render_template(self.template)


if __name__ == "__main__":
    node = MkJinjaTemplate.with_default_context("requirements.md")
    print(node)

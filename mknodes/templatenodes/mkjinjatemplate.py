from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkJinjaTemplate(mknode.MkNode):
    """Node representing a jinja template."""

    ICON = "material/function"
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

    @property
    def infoprovider(self):
        from mknodes.plugin import infocollector

        if self.associated_project:
            env = self.associated_project.infocollector
        else:
            env = infocollector.InfoCollector(undefined="strict", load_templates=True)
        # env.variables["parent"] = self.parent
        return env

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkJinjaTemplate(template="requirements.md")
        page += mknodes.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        variables = self.variables | {"parent": self.parent}
        self.infoprovider.set_mknodes_filters(parent=self)
        return self.infoprovider.render_template(self.template, variables)


if __name__ == "__main__":
    import mknodes

    proj = mknodes.Project.for_mknodes()
    node = MkJinjaTemplate(
        "requirements.md",
        project=proj,
        parent=mknodes.MkCode("test2"),
    )
    print(node)

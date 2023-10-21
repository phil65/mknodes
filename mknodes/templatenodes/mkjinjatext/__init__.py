from __future__ import annotations

from typing import Any

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkJinjaText(mkcontainer.MkContainer):
    """Node representing a jinja text template.

    Renders template strings with the context-aware MkNodes jinja environment.
    Rendered nodes become virtual children of this node.
    Additional variables can be passed to the template render process.
    """

    ICON = "simple/jinja"
    STATUS = "new"

    def __init__(
        self,
        text: str,
        *,
        variables: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Jinja text name.
            variables: Variables to use for rendering
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.text = text
        self.variables = variables or {}

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            text=self.text,
            variables=self.variables,
            _filter_empty=True,
        )

    @property
    def items(self):
        self.env.render_string(self.text, variables=self.variables)
        return self.env.rendered_nodes

    @items.setter
    def items(self, val):
        pass

    @classmethod
    def create_example_page(cls, page):
        node = MkJinjaText(text="Test")
        page += node

    def _to_markdown(self) -> str:
        return self.env.render_string(self.text, variables=self.variables)


if __name__ == "__main__":
    node = MkJinjaText("nodes_index.jinja")
    print(node.get_resources())

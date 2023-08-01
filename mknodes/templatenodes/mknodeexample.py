from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mkcontainer, mknode, mktabcontainer
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkNodeExample(mkcontainer.MkContainer):
    """MkCritic block."""

    ICON = "simple/shieldsdotio"

    def __init__(
        self,
        node: mknode.MkNode,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            node: Node to show an example for
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.node = node

    def __repr__(self):
        return helpers.get_repr(self, node=self.node)

    def _to_markdown(self) -> str:
        repr_node = mkcode.MkCode(repr(self.node))
        markdown_node = mkcode.MkCode(str(self.node))
        tabs = dict(repr=repr_node, markdown=markdown_node, rendered=self.node)
        tab_node = mktabcontainer.MkTabbed(tabs)
        return str(tab_node)

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.metadata["status"] = "new"
        example_node = mknodes.MkAdmonition("Some text")
        node = MkNodeExample(node=example_node)
        page += node
        page += MkNodeExample(node)


if __name__ == "__main__":
    import mknodes

    example_node = mknodes.MkAdmonition("Some text")
    node = MkNodeExample(node=example_node)
    print(node)

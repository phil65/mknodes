from __future__ import annotations

import logging
import textwrap

from typing import Any

from mknodes.basenodes import mkcode, mknode, mktabcontainer, mktext
from mknodes.pages import mkpage
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkReprRawRendered(mktabcontainer.MkTabbed):
    """MkCritic block."""

    ICON = "material/presentation"

    def __init__(
        self,
        node: mknode.MkNode,
        indent: bool = False,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            node: Node to show an example for
            kwargs: Keyword arguments passed to parent
            indent: Whether the markdown tab should be indented (for escaping)
        """
        repr_node = mkcode.MkCode(repr(node))
        if indent:
            markdown_node = mkcode.MkCode(textwrap.indent(str(node), prefix="    "))
        else:
            markdown_node = mkcode.MkCode(str(node))
        # TODO: hack: without doing this, we get issues because the page becomes
        # part of the tree. Perhaps add a setting for MkPages to be only-virtual?
        # Needs a general concept in regards to re-parenting. (should base nodes
        # be allowed to have pages as children?)
        if isinstance(node, mkpage.MkPage):
            node = mktext.MkText(node)
        self.node = node
        tabs = dict(Repr=repr_node, Markdown=markdown_node, Rendered=node)
        super().__init__(tabs=tabs, select_tab=2, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, node=self.node)

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"  # for the small icon in the left menu
        example_node = mknodes.MkAdmonition("Some text")
        node = MkReprRawRendered(node=example_node)
        page += node
        page += MkReprRawRendered(node)


if __name__ == "__main__":
    import mknodes

    example_node = mknodes.MkAdmonition("Some text")
    node = MkReprRawRendered(node=example_node)
    print(node)

from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mknode, mktabcontainer, mktabs
from mknodes.pages import mkpage
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkReprRawRendered(mktabcontainer.MkTabbed):
    """MkCritic block."""

    ICON = "material/presentation"

    def __init__(self, node: mknode.MkNode, **kwargs: Any):
        """Constructor.

        Arguments:
            node: Node to show an example for
            kwargs: Keyword arguments passed to parent
        """
        self.node = node
        super().__init__(tabs={}, select_tab=2, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, node=self.node)

    @property
    def items(self):
        # TODO: hack: without doing this, we get issues because the page becomes
        # part of the tree. Perhaps add a setting for MkPages to be only-virtual?
        # Needs a general concept in regards to re-parenting. (should base nodes
        # be allowed to have pages as children?)
        tabs: dict[str, str | mknode.MkNode] = dict(  # type: ignore[annotation-unchecked]
            Repr=mkcode.MkCode(repr(self.node)),
            Markdown=mkcode.MkCode(self.prep(self.node), language="markdown"),
            Rendered=str(self.node),
        )
        if len(self.node.children) > 0:
            lines = [f"{level * '    '} {n!r}" for level, n in self.node.iter_nodes()]
            tabs["Repr tree"] = mkcode.MkCode("\n".join(lines))
        items = [mktabs.MkTab(k, v, parent=self) for k, v in tabs.items()]
        items[0].new = True
        return items

    @items.setter
    def items(self, value):
        pass

    def prep(self, node):
        # node.parent = self
        if isinstance(node, mkpage.MkPage):
            node = node.__copy__()
            node.parent = None
            node.path = f"__{node.path}"
        return node

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

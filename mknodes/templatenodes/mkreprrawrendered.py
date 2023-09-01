from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkcode, mknode, mktabcontainer, mktabs
from mknodes.templatenodes import mktreeview
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkReprRawRendered(mktabcontainer.MkTabbed):
    """Node showing a tabbed bock to visualize a node.

    It contains a tab for the repr, one for the rendered output,
    one for the markdown and a Repr tree in case the node has children.
    """

    ICON = "material/presentation"

    def __init__(
        self,
        node: mknode.MkNode,
        select_tab: int | str | None = 2,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            node: Node to show an example for
            select_tab: Tab which should be selected initially
            kwargs: Keyword arguments passed to parent
        """
        self.node = node
        super().__init__(tabs={}, select_tab=select_tab, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, node=self.node)

    @property
    def items(self):
        # TODO: hack: without doing this, we get issues because the page becomes
        # part of the tree. Perhaps add a setting for MkPages to be only-virtual?
        # Needs a general concept in regards to re-parenting. (should base nodes
        # be allowed to have pages as children?)
        tabs: dict[str, str | mknode.MkNode] = dict(  # type: ignore[annotation-unchecked]
            Repr=mkcode.MkCode(repr(self.node)),
            Markdown=mkcode.MkCode(self.node, language="markdown"),
            Rendered=self.node.__copy__(),
        )
        if len(self.node.children) > 0:
            tabs["Repr tree"] = mktreeview.MkTreeView(self.node)
        items = [mktabs.MkTab(k, v, parent=self) for k, v in tabs.items()]
        items[0].new = True
        if self.select_tab is not None:
            pos = (
                self._get_tab_pos(self.select_tab)
                if isinstance(self.select_tab, str)
                else self.select_tab
            )
            items[pos].select = True
        return items

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        example_node = mknodes.MkAdmonition("Some text")
        node = MkReprRawRendered(node=example_node)
        page += node
        page += MkReprRawRendered(node)


if __name__ == "__main__":
    import mknodes

    example_node = mknodes.MkAdmonition("Some text")
    node = MkReprRawRendered(node=example_node)
    print(node)

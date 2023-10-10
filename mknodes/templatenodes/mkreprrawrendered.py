from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode, mktabcontainer, mktabs
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkReprRawRendered(mktabcontainer.MkTabbed):
    """Node showing a tabbed block to visualize a node in different representations.

    It contains a tab for the repr, one for the rendered output,
    one for the markdown and a Repr tree in case the node has children.
    """

    ICON = "material/presentation"

    def __init__(
        self,
        node: mknode.MkNode,
        select_tab: int | str | None = 3,
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
        import mknodes as mk

        html_node = self.node.__copy__()
        html_node.as_html = True
        tabs: dict[str, str | mk.MkNode] = dict(  # type: ignore[annotation-unchecked]
            Repr=mk.MkCode(repr(self.node)),
            Raw=mk.MkCode(self.node, language="markdown"),
            Html=mk.MkCode(html_node, language="html"),
            Rendered=self.node.__copy__(),
        )
        if len(self.node.children) > 0:
            tabs["Repr tree"] = mk.MkTreeView(self.node)
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

    @classmethod
    def create_example_page(cls, page):
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

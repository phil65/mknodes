from __future__ import annotations

from typing import Any, TYPE_CHECKING

from mknodes.templatenodes import mktemplate

if TYPE_CHECKING:
    from mknodes.basenodes import mknode


class MkReprRawRendered(mktemplate.MkTemplate):
    """Node showing a tabbed block to visualize a node in different representations.

    It contains a tab for the repr, one for the rendered output,
    one for the markdown and a Repr tree in case the node has children.
    The node can also be a string with a jinja macro returning an MkNode.
    In that case a "Jinja" tab containing the macro is prepended to the other tabs.
    """

    ICON = "material/presentation"

    def __init__(self, node: mknode.MkNode | str | None = None, **kwargs: Any):
        """Constructor.

        Arguments:
            node: Node to show an example for
            kwargs: Keyword arguments passed to parent
        """
        self._node = node
        super().__init__("output/markdown/template", **kwargs)

    @property
    def node(self):
        match self._node:
            case None:
                return None
            case str():
                self.env.render_string(self._node)
                return self.env.rendered_children[0]
            case _:
                return self._node


if __name__ == "__main__":
    import mknodes as mk

    example_node = mk.MkAdmonition("Some text")
    node = MkReprRawRendered(node=example_node)
    print(node)

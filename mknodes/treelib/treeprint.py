from __future__ import annotations

from collections.abc import Iterable
import logging

from mknodes.data import treestyles
from mknodes.treelib import node
from mknodes.utils import connector


logger = logging.getLogger(__name__)


def get_tree_repr(
    tree: node.Node,
    max_depth: int | None = None,
    style: treestyles.TreeStyleStr | tuple | None = None,
    attr_list: list[str] | None = None,
    attr_bracket: list[str] | None = None,
) -> str:
    if style is None:
        style = "ascii"
    if attr_list is None:
        attr_list = []
    if attr_bracket is None:
        attr_bracket = ["[", "]"]
    lines = [
        f"{pre_str}{fill_str}{_node!r}"
        for pre_str, fill_str, _node in yield_tree(
            tree=tree,
            max_depth=max_depth,
            style=style,
        )
    ]
    return repr(tree) + "\n" + "\n".join(lines[1:])


def yield_tree(
    tree: node.Node,
    max_depth: int | None = None,
    style: treestyles.TreeStyleStr | tuple = "const",
) -> Iterable[tuple[str, str, node.Node]]:
    if isinstance(style, tuple):
        custom_style: list[str] = list(style)
        parent_last, filename_middle, filename_last = custom_style
        gap_str = " " * len(parent_last)
    else:
        style_obj = treestyles.STYLES[style]
        parent_last = style_obj.parent_last
        filename_middle = style_obj.filename_middle
        filename_last = style_obj.filename_last
        gap_str = style_obj.parent_middle
    unclosed_depth = set()
    initial_depth = tree.depth
    for _node in node.preorder_iter(tree, max_depth=max_depth):
        pre_str = ""
        fill_str = ""
        if not _node.is_root:
            node_depth = _node.depth - initial_depth

            # Get fill_str (filename_middle or filename_last)
            if _node.right_sibling:
                unclosed_depth.add(node_depth)
                fill_str = filename_middle
            else:
                if node_depth in unclosed_depth:
                    unclosed_depth.remove(node_depth)
                fill_str = filename_last

            pre_str = "".join(
                parent_last if _depth in unclosed_depth else gap_str
                for _depth in range(1, node_depth)
            )
        yield pre_str, fill_str, _node


class NodeConnector(connector.Connector):
    def get_children(self, item):
        return item.children

    def get_id(self, item):
        # id() would be enough, but name is sometimes useful for debugging.
        return f"{type(item).__name__}_{id(item)}"

    def get_title(self, item) -> str:
        return f"{type(item).__name__}"


def to_tree_graph(node, direction: str = "TD") -> str:
    """Returns markdown to display a tree graph of this node and all subnodes.

    Arguments:
        node: node to get a graph for
        direction: Direction of resulting graph
    """
    item_str = NodeConnector([node]).get_graph_connection_text()
    text = f"graph {direction}\n{item_str}"
    return f"```mermaid\n{text}\n```"

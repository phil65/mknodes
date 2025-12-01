from __future__ import annotations

from typing import TYPE_CHECKING

from mknodes.utils import connector, log


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


class NodeConnector(connector.Connector["mk.MkNode"]):
    def get_children(self, item: mk.MkNode):  # pyright: ignore[reportIncompatibleMethodOverride]
        return item.get_children()

    def get_id(self, item: mk.MkNode) -> str:
        # id() would be enough, but name is sometimes useful for debugging.
        return f"{type(item).__name__}_{id(item)}"

    def get_title(self, item: mk.MkNode) -> str:
        return f"{type(item).__name__}"


def to_tree_graph(node: mk.MkNode, direction: str = "TD") -> str:
    """Returns markdown to display a tree graph of this node and all subnodes.

    Args:
        node: node to get a graph for
        direction: Direction of resulting graph
    """
    item_str = NodeConnector([node]).get_graph_connection_text()
    text = f"graph {direction}\n{item_str}"
    return f"```mermaid\n{text}\n```"

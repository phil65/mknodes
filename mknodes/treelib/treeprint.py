from __future__ import annotations

from mknodes.utils import connector, log


logger = log.get_logger(__name__)


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

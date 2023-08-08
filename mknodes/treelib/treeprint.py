from __future__ import annotations

from collections.abc import Iterable
import logging

from mknodes.treelib import node
from mknodes.utils import connector


logger = logging.getLogger(__name__)


AVAILABLE_STYLES = {
    "ansi": ("|   ", "|-- ", "`-- "),
    "ascii": ("|   ", "|-- ", "+-- "),
    "const": ("\u2502   ", "\u251c\u2500\u2500 ", "\u2514\u2500\u2500 "),
    "const_bold": ("\u2503   ", "\u2523\u2501\u2501 ", "\u2517\u2501\u2501 "),
    "rounded": ("\u2502   ", "\u251c\u2500\u2500 ", "\u2570\u2500\u2500 "),
    "double": ("\u2551   ", "\u2560\u2550\u2550 ", "\u255a\u2550\u2550 "),
    "spaces": ("    ", "    ", "    "),
    "custom": ("", "", ""),
}


def get_tree_repr(
    tree: node.Node,
    max_depth: int | None = None,
    style: str | tuple | None = None,
    attr_list: list[str] | None = None,
    attr_bracket: list[str] | None = None,
) -> str:
    """Get tree repr.

    >>> get_tree_repr(root)
    a
    ├── b
    │   ├── d
    │   └── e
    └── c

    >>> get_tree_repr(root, max_depth=2)
    a
    ├── b
    └── c

    **Printing Attributes**

    >>> get_tree_repr(root, attr_list=["age"])
    a [age=90]
    ├── b [age=65]
    │   ├── d [age=40]
    │   └── e [age=35]
    └── c [age=60]

    >>> get_tree_repr(root, attr_list=["age"], attr_bracket=["*(", ")"])
    a *(age=90)
    ├── b *(age=65)
    │   ├── d *(age=40)
    │   └── e *(age=35)
    └── c *(age=60)

    **Available Styles**

    >>> get_tree_repr(root, style="ansi")
    a
    |-- b
    |   |-- d
    |   `-- e
    `-- c

    >>> get_tree_repr(root, style="ascii")
    a
    |-- b
    |   |-- d
    |   +-- e
    +-- c

    >>> get_tree_repr(root, style="const")
    a
    ├── b
    │   ├── d
    │   └── e
    └── c

    >>> get_tree_repr(root, style="const_bold")
    a
    ┣━━ b
    ┃   ┣━━ d
    ┃   ┗━━ e
    ┗━━ c

    >>> get_tree_repr(root, style="rounded")
    a
    ├── b
    │   ├── d
    │   ╰── e
    ╰── c

    >>> get_tree_repr(root, style="double")
    a
    ╠══ b
    ║   ╠══ d
    ║   ╚══ e
    ╚══ c

    Args:
        tree: tree to print
        max_depth: maximum depth of tree to print, based on `depth` attribute
        style: style of print, defaults to abstract style
        attr_list: list of node attributes to print
        attr_bracket: open and close bracket for `all_attrs` or `attr_list`
    """
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
    return "\n".join(lines)


def yield_tree(
    tree: node.Node,
    max_depth: int | None = None,
    style: str | tuple = "const",
) -> Iterable[tuple[str, str, node.Node]]:
    """Generator method for customizing printing of tree, starting from `tree`.

    - Several styles: `ansi`, `ascii`, `const`, `rounded`, `double`,

    **Printing tree**

    >>> root = Node("a", age=90)
    >>> b = Node("b", age=65, parent=root)
    >>> c = Node("c", age=60, parent=root)
    >>> d = Node("d", age=40, parent=b)
    >>> e = Node("e", age=35, parent=b)
    >>> for branch, stem, node in yield_tree(root):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    ├── b
    │   ├── d
    │   └── e
    └── c

    >>> for branch, stem, node in yield_tree(root, max_depth=2):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    ├── b
    └── c

    **Available Styles**

    >>> for branch, stem, node in yield_tree(root, style="ansi"):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    |-- b
    |   |-- d
    |   `-- e
    `-- c

    >>> for branch, stem, node in yield_tree(root, style="ascii"):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    |-- b
    |   |-- d
    |   +-- e
    +-- c

    >>> for branch, stem, node in yield_tree(root, style="const"):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    ├── b
    │   ├── d
    │   └── e
    └── c

    >>> for branch, stem, node in yield_tree(root, style="const_bold"):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    ┣━━ b
    ┃   ┣━━ d
    ┃   ┗━━ e
    ┗━━ c

    >>> for branch, stem, node in yield_tree(root, style="rounded"):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    ├── b
    │   ├── d
    │   ╰── e
    ╰── c

    >>> for branch, stem, node in yield_tree(root, style="double"):
    ...     print(f"{branch}{stem}{node.node_name}")
    a
    ╠══ b
    ║   ╠══ d
    ║   ╚══ e
    ╚══ c

    **Printing Attributes**

    >>> for branch, stem, node in yield_tree(root, style="const"):
    ...     print(f"{branch}{stem}{node.node_name} [age={node.age}]")
    a [age=90]
    ├── b [age=65]
    │   ├── d [age=40]
    │   └── e [age=35]
    └── c [age=60]

    Args:
        tree: tree to print
        max_depth: maximum depth of tree to print, based on `depth` attribute,
        style: style of print, defaults to abstract style
    """
    if isinstance(style, tuple):
        custom_style: list[str] = list(style)
        style = "custom"
    else:
        custom_style = []
    tree = tree.__copy__()
    if not tree.is_root:
        tree.parent = None
    if style == "custom":
        style_stem, style_branch, style_stem_final = custom_style
    else:
        style_stem, style_branch, style_stem_final = AVAILABLE_STYLES[style]

    if not len(style_stem) == len(style_branch) == len(style_stem_final):
        msg = "Need same length for style elements"
        raise ValueError(msg)
    gap_str = " " * len(style_stem)
    unclosed_depth = set()
    initial_depth = tree.depth
    for _node in node.preorder_iter(tree, max_depth=max_depth):
        pre_str = ""
        fill_str = ""
        if not _node.is_root:
            node_depth = _node.depth - initial_depth

            # Get fill_str (style_branch or style_stem_final)
            if _node.right_sibling:
                unclosed_depth.add(node_depth)
                fill_str = style_branch
            else:
                if node_depth in unclosed_depth:
                    unclosed_depth.remove(node_depth)
                fill_str = style_stem_final

            pre_str = "".join(
                style_stem if _depth in unclosed_depth else gap_str
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

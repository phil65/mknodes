from __future__ import annotations

import copy
from typing import TYPE_CHECKING, Any, Self

from mknodes.data import treestyles
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    from collections.abc import Callable, Iterable, Iterator, Sequence
    import types


logger = log.get_logger(__name__)


class Node:
    """A Node class that can be used to build trees."""

    # __slots__ = ("parent", "children")

    def __init__(self, parent: Self | None = None):
        self._parent = parent
        self.children: list[Self] = []

    def __repr__(self):
        return reprhelpers.get_nondefault_repr(self)

    def __iter__(self) -> Iterator[Self]:
        yield from self.children

    def __rshift__(self, other: Self):
        """Set children using >> bitshift operator for self >> other.

        Args:
            other (Self): other node, children
        """
        other.parent = self

    def __lshift__(self, other: Self):
        """Set parent using << bitshift operator for self << other.

        Args:
            other (Self): other node, parent
        """
        self._parent = other

    @property
    def parent(self):
        """The parent node of this node."""
        return self._parent

    @parent.setter
    def parent(self, value):
        # if self._parent is not None and self._parent != value:
        #     msg = f"{self!r}: parent {self._parent!r} replaced with {value!r}"
        #     logger.debug(msg)
        self._parent = value

    def __copy__(self, **kwargs: Any) -> Self:
        """Shallow copy self."""
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        obj.__dict__.update(kwargs)
        return obj

    def __deepcopy__(self, memo):
        cls = self.__class__
        result = cls.__new__(cls)
        memo[id(self)] = result
        for k, v in self.__dict__.items():
            setattr(result, k, copy.deepcopy(v, memo))
        return result

    def append_child(self, item: Self):
        """Append a node as a child.

        Args:
            item: Node to add as a child
        """
        item.parent = self
        self.children.append(item)

    def insert_children(self, idx: int, items: Sequence[Self]):
        """Insert a list of child nodes at given index.

        Args:
            idx: The index of insertion
            items: A sequence of nodes to add as children
        """
        self.children[idx:idx] = items
        for item in items:
            item.parent = self

    @property
    def ancestors(self) -> Iterable[Self]:
        """Get iterator to yield all ancestors of self, does not include self."""
        node = self
        while (node := node.parent) is not None:
            yield node

    @property
    def descendants(self) -> Iterable[Self]:
        """Get iterator to yield all descendants of self, does not include self."""
        yield from preorder_iter(self, filter_condition=lambda _node: _node != self)

    def is_descendant_of(self, kls: type | types.UnionType) -> bool:
        """Returns True if any ancestor is of given type.

        Args:
            kls: The class (union) the check the ancestors for
        """
        return any(isinstance(i, kls) for i in self.ancestors)

    @property
    def leaves(self) -> Iterable[Self]:
        """Get iterator to yield all leaf nodes from self."""
        yield from preorder_iter(self, filter_condition=lambda _node: _node.is_leaf)

    @property
    def siblings(self) -> Iterable[Self]:
        """Get siblings of self."""
        if self._parent is None:
            return ()
        return tuple(child for child in self._parent.children if child is not self)

    @property
    def left_sibling(self) -> Self | None:
        """Get sibling left of self."""
        if not self._parent:
            return None
        children = self._parent.children
        if child_idx := children.index(self):
            return children[child_idx - 1]
        return None

    @property
    def right_sibling(self) -> Self | None:
        """Get sibling right of self."""
        if not self._parent:
            return None
        children = self._parent.children
        child_idx = children.index(self)
        if child_idx + 1 < len(children):
            return children[child_idx + 1]
        return None

    @property
    def node_path(self) -> Iterable[Self]:
        """Get tuple of nodes starting from root."""
        if self._parent is None:
            return [self]
        return (*list(self._parent.node_path), self)

    @property
    def is_root(self) -> bool:
        """Get indicator if self is root node."""
        return self._parent is None

    @property
    def is_leaf(self) -> bool:
        """Get indicator if self is leaf node."""
        return not list(self.children)

    @property
    def is_first_child(self) -> bool:
        """Get indicator if self is first child of parent."""
        return not bool(self.left_sibling)

    @property
    def is_last_child(self) -> bool:
        """Get indicator if self is last child of parent."""
        return not bool(self.right_sibling)

    @property
    def root(self) -> Self:
        """Get root node of tree."""
        return self if self._parent is None else self._parent.root

    @property
    def depth(self) -> int:
        """Get depth of self, indexing starts from 1."""
        return 1 if self._parent is None else self._parent.depth + 1

    @property
    def max_depth(self) -> int:
        """Get maximum depth from root to leaf node."""
        return max(
            [self.root.depth] + [node.depth for node in list(self.root.descendants)],
        )

    def row(self) -> int:  # sourcery skip: assign-if-exp
        """Return the position of this node inside the parent's children list."""
        if self._parent:
            return self._parent.children.index(self)  # type: ignore
        return 0

    def pformat(self, indent: int = 0, max_depth: int | None = None):
        lines = [
            _indent * "    " + repr(child_item)
            for _indent, child_item in self.iter_nodes(indent, max_depth)
        ]
        return "\n".join(lines)

    def iter_nodes(self, indent: int = 0, max_depth: int | None = None):
        """Iterate over all nodes, including self and children.

        Yields current-depth-node tuples.

        Args:
            indent: The start "level". The first element of the returned tuple will be
                    relative to this
            max_depth: The max depth to iterate
        """
        if max_depth is not None and indent > max_depth:
            return
        yield indent, self
        for child_item in self.children:
            yield from child_item.iter_nodes(indent + 1)

    def get_tree_repr(
        self,
        max_depth: int | None = None,
        style: treestyles.TreeStyleStr | tuple[str, str, str, str] | None = None,
        detailed: bool = True,
    ) -> str:
        def formatter(x: object) -> str:
            return repr(x) if detailed else x.__class__.__name__

        lines = [
            f"{pre_str}{fill_str}{formatter(_node)}"
            for pre_str, fill_str, _node in self._yield_tree(
                max_depth=max_depth,
                style=style or "ascii",
            )
        ]
        return self.__class__.__name__ + "\n" + "\n".join(lines[1:])

    def _yield_tree(
        self,
        max_depth: int | None = None,
        style: treestyles.TreeStyleStr | tuple[str, ...] = "const",
    ) -> Iterable[tuple[str, str, Node]]:
        """Yield a tuple for prettyprinting the tree.

        Tuple consists of two strings to be used as a prefix, and the node itself.

        Args:
            max_depth: The maxium depth of nodes to yield
            style: The prefix style.
        """
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
        unclosed_depth: set[int] = set()
        initial_depth = self.depth
        for _node in preorder_iter(self, max_depth=max_depth):
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

    # def displayable(self, style_name: treestyles.TreeStyleStr = "ascii"):
    #     style = treestyles.STYLES[style_name]
    #     if self.parent is None:
    #         return repr(self)
    #     prefix = style.filename_last if self.is_last_child else style.filename_middle
    #     parts = [f"{prefix!s} {self!r}"]
    #     parent = self.parent
    #     while parent and parent.parent is not None:
    #         part = style.parent_last if parent.is_last_child else style.parent_middle
    #         parts.append(part)
    #         parent = parent.parent
    #     return "".join(reversed(parts))

    # def get_tree_repr(self, style: treestyles.TreeStyleStr = "ascii"):
    #     nodes = [self, *list(self.descendants)]
    #     return "\n".join(i.displayable(style) for i in nodes)


def preorder_iter(
    tree: Node,
    filter_condition: Callable[[Node], bool] | None = None,
    stop_condition: Callable[[Node], bool] | None = None,
    max_depth: int | None = None,
) -> Iterable[Node]:
    """Iterate through all children of a tree.

    It is topologically sorted because a parent node is processed before its child nodes.

    a
    ├── b
    │   ├── d
    │   └── e
    │       ├── g
    │       └── h
    └── c
        └── f

    >>> [node.node_name for node in preorder_iter(root)]
    ['a', 'b', 'd', 'e', 'g', 'h', 'c', 'f']

    Args:
        tree: input tree
        filter_condition: function that takes in node as argument
        stop_condition: function that takes in node as argument
        max_depth: maximum depth of iteration, based on `depth` attribute
    """
    if (not max_depth or tree.depth <= max_depth) and (
        not stop_condition or not stop_condition(tree)
    ):
        if not filter_condition or filter_condition(tree):
            yield tree
        for child in tree.children:
            yield from preorder_iter(child, filter_condition, stop_condition, max_depth)


if __name__ == "__main__":
    node = Node()
    sub = Node(parent=node)
    subsub = Node(parent=sub)
    node.children = [sub, subsub]

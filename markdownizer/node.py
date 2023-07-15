from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
import logging
import re

from typing_extensions import Self

from markdownizer import utils


_MAXCACHE = 20

logger = logging.getLogger(__name__)


class BaseResolver:
    _match_cache = {}

    def __init__(self, ignore_case: bool = False):
        """Base resolver. Subclass to get glob functionality.

        Keyword Args:
            name (str): Name of the node attribute to be used for resolving
            ignore_case (bool): Enable case insensisitve handling.
        """
        super().__init__()
        self.ignore_case = ignore_case

    def get_parent(self, node):
        return NotImplemented

    def get_children(self, node):
        return NotImplemented

    def get_attribute(self, node):
        return NotImplemented

    def get_root(self, node):
        prev = node
        while node:
            node = self.get_parent(node)
            prev = node
        return prev

    def get_separator(self, node) -> str:
        return "/"

    def get(self, path: str, root_node):
        """Return instance at `path`.

        An example module tree:

        >>> top = Node("top", parent=None)
        >>> sub0 = Node("sub0", parent=top)
        >>> sub0sub0 = Node("sub0sub0", parent=sub0)
        >>> sub0sub1 = Node("sub0sub1", parent=sub0)
        >>> sub1 = Node("sub1", parent=top)

        A resolver using the `name` attribute:

        >>> r = Resolver('name')

        Relative paths:

        >>> r.get(top, "sub0/sub0sub0")
        Node('/top/sub0/sub0sub0')
        >>> r.get(sub1, "..")
        Node('/top')
        >>> r.get(sub1, "../sub0/sub0sub1")
        Node('/top/sub0/sub0sub1')
        >>> r.get(sub1, ".")
        Node('/top/sub1')
        >>> r.get(sub1, "")
        Node('/top/sub1')
        >>> r.get(top, "sub2")
        Traceback (most recent call last):
          ...
        ChildResolverError: Node('/top') has no child sub2.
        Children are: 'sub0', 'sub1'.

        Absolute paths:

        >>> r.get(sub0sub0, "/top")
        Node('/top')
        >>> r.get(sub0sub0, "/top/sub0")
        Node('/top/sub0')
        >>> r.get(sub0sub0, "/")
        Traceback (most recent call last):
          ...
        ResolverError: root node missing. root is '/top'.
        >>> r.get(sub0sub0, "/bar")
        Traceback (most recent call last):
          ...
        ResolverError: unknown root node '/bar'. root is '/top'.

        Going above the root node raises a :any:`RootResolverError`:

        >>> r.get(top, "..")
        Traceback (most recent call last):
            ...
        RootResolverError: Cannot go above root node Node('/top')

        .. note:: Please not that :any:`get()` returned `None` in exactly that case above,
                  which was a bug until version 1.8.1.

        Case insensitive matching:

        >>> r.get(top, '/TOP')
        Traceback (most recent call last):
            ...
        ResolverError: unknown root node '/TOP'. root is '/top'.

        >>> r = Resolver('name', ignore_case=True)
        >>> r.get(top, '/TOp')
        Node('/top')
        """
        node, parts = self.__start(root_node, path, self.__cmp)
        for part in parts:
            if part == "..":
                parent = self.get_parent(node)
                if parent is None:
                    raise RootResolverError(node)
                node = parent
            elif part not in ("", "."):
                node = self.__get(node, part)
        return node

    def __get(self, node, name):
        for child in self.get_children(node):
            if self.__cmp(self.get_attribute(child), str(name)):
                return child
        names = [repr(self.get_attribute(c)) for c in self.get_children(node)]
        raise ChildResolverError(node, name, names)

    def glob(self, path: str, root_node):
        """Return instances at `path` supporting wildcards.

        Behaves identical to :any:`get`, but accepts wildcards and returns
        a list of found nodes.

        * `*` matches any characters, except '/'.
        * `?` matches a single character, except '/'.

        An example module tree:

        >>> top = Node("top", parent=None)
        >>> sub0 = Node("sub0", parent=top)
        >>> sub0sub0 = Node("sub0", parent=sub0)
        >>> sub0sub1 = Node("sub1", parent=sub0)
        >>> sub1 = Node("sub1", parent=top)
        >>> sub1sub0 = Node("sub0", parent=sub1)

        A resolver using the `name` attribute:

        >>> r = Resolver('name')

        Relative paths:

        >>> r.glob(top, "sub0/sub?")
        [Node('/top/sub0/sub0'), Node('/top/sub0/sub1')]
        >>> r.glob(sub1, ".././*")
        [Node('/top/sub0'), Node('/top/sub1')]
        >>> r.glob(top, "*/*")
        [Node('/top/sub0/sub0'), Node('/top/sub0/sub1'), Node('/top/sub1/sub0')]
        >>> r.glob(top, "*/sub0")
        [Node('/top/sub0/sub0'), Node('/top/sub1/sub0')]
        >>> r.glob(top, "sub1/sub1")
        Traceback (most recent call last):
            ...
        ChildResolverError: Node('/top/sub1') has no child sub1.
        Children are: 'sub0'.

        Non-matching wildcards are no error:

        >>> r.glob(top, "bar*")
        []
        >>> r.glob(top, "sub2")
        Traceback (most recent call last):
          ...
        ChildResolverError: Node('/top') has no child sub2.
        Children are: 'sub0', 'sub1'.

        Absolute paths:

        >>> r.glob(sub0sub0, "/top/*")
        [Node('/top/sub0'), Node('/top/sub1')]
        >>> r.glob(sub0sub0, "/")
        Traceback (most recent call last):
          ...
        ResolverError: root node missing. root is '/top'.
        >>> r.glob(sub0sub0, "/bar")
        Traceback (most recent call last):
          ...
        ResolverError: unknown root node '/bar'. root is '/top'.

        Going above the root node raises a :any:`RootResolverError`:

        >>> r.glob(top, "..")
        Traceback (most recent call last):
            ...
        RootResolverError: Cannot go above root node Node('/top')
        """
        node, parts = self.__start(root_node, path, self.__match)
        return self.__glob(node, parts)

    def __start(self, node, path: str, cmp_):
        sep = self.get_separator(node)
        parts = path.split(sep)
        # resolve root
        if path.startswith(sep):
            node = self.get_root(node)
            rootpart = self.get_attribute(node)
            parts.pop(0)
            if not parts[0]:
                msg = f"root node missing. root is '{sep}{rootpart}'."
                raise ResolverError(node, "", msg)
            if not cmp_(rootpart, parts[0]):
                msg = f"unknown root node '{sep}{parts[0]}'. root is '{sep}{rootpart}'."
                raise ResolverError(node, "", msg)
            parts.pop(0)
        return node, parts

    def __glob(self, node, parts):
        assert node is not None
        nodes = []
        if parts:
            name = parts[0]
            remainder = parts[1:]
            # handle relative
            if name == "..":
                parent = self.get_parent(node)
                if parent is None:
                    raise RootResolverError(node)
                else:
                    nodes += self.__glob(parent, remainder)
            elif name in ("", "."):
                nodes += self.__glob(node, remainder)
            elif matches := self.__find(node, name, remainder):
                nodes += matches
            elif self.is_wildcard(name):
                nodes += matches
            else:
                names = [repr(self.get_attribute(c)) for c in self.get_children(node)]
                raise ChildResolverError(node, name, names)
        else:
            nodes = [node]
        return nodes

    def __find(self, node, pat, remainder):
        matches = []
        for child in self.get_children(node):
            name = self.get_attribute(child)
            try:
                if self.__match(name, pat):
                    if remainder:
                        matches += self.__glob(child, remainder)
                    else:
                        matches.append(child)
            except ResolverError as exc:  # noqa: PERF203
                if not self.is_wildcard(pat):
                    raise exc
        return matches

    @staticmethod
    def is_wildcard(path: str) -> bool:
        """Return `True` is a wildcard."""
        return "?" in path or "*" in path

    def __match(self, name, pat):
        k = (pat, self.ignore_case)
        try:
            re_pat = self._match_cache[k]
        except KeyError:
            res = self.__translate(pat)
            if len(self._match_cache) >= _MAXCACHE:
                self._match_cache.clear()
            flags = 0
            if self.ignore_case:
                flags |= re.IGNORECASE
            self._match_cache[k] = re_pat = re.compile(res, flags=flags)
        return re_pat.match(name) is not None

    def __cmp(self, name, pat):
        return name.upper() == pat.upper() if self.ignore_case else name == pat

    @staticmethod
    def __translate(pat):
        re_pat = ""
        for char in pat:
            if char == "*":
                re_pat += ".*"
            elif char == "?":
                re_pat += "."
            else:
                re_pat += re.escape(char)
        return f"(?ms){re_pat}" + r"\Z"  # noqa: ISC003


class ResolverError(RuntimeError):
    def __init__(self, node, child, msg):
        """Resolve Error at `node` handling `child`."""
        super().__init__(msg)
        self.node = node
        self.child = child


class RootResolverError(ResolverError):
    def __init__(self, root):
        """Root Resolve Error, cannot go above root node."""
        msg = f"Cannot go above root node {root!r}"
        super().__init__(root, None, msg)


class ChildResolverError(ResolverError):
    def __init__(self, node, child, names):
        """Child Resolve Error at `node` handling `child`."""
        msg = "{!r} has no child {}. Children are: {}.".format(
            node, child, ", ".join(names)
        )
        super().__init__(node, child, msg)


logger = logging.getLogger(__name__)


class NodeResolver(BaseResolver):
    def __init__(self, path_attr: str = "obj", ignore_case: bool = False):
        """Resolve any `Node` paths using attribute `path_attr`.

        Arguments:
            path_attr: Name of the node attribute to be used for resolving
            ignore_case: Enable case insensisitve handling.
        """
        super().__init__(ignore_case=ignore_case)
        self.path_attr = path_attr

    def get_parent(self, node):
        return node.parent

    def get_children(self, node):
        return node.children

    def get_root(self, node):
        return node.root

    def get_attribute(self, node):
        return getattr(node, self.path_attr)


class BaseNode:
    """A Node class that can be used to build trees."""

    # __slots__ = ("parent_item", "children")

    def __init__(self, parent: Self | None = None):
        self.parent_item = parent
        self.children: list[BaseNode] = []

    def __repr__(self):
        return utils.get_repr(self)

    def __iter__(self) -> Iterator[Self]:
        return iter(self.children)

    def __getitem__(self, index: int) -> Self:
        return self.children[index]

    def __rshift__(self, other: Self):
        """Set children using >> bitshift operator for self >> other.

        Args:
            other (Self): other node, children
        """
        other.parent_item = self

    def __lshift__(self, other: Self):
        """Set parent using << bitshift operator for self << other.

        Args:
            other (Self): other node, parent
        """
        self.parent_item = other

    def __copy__(self) -> Self:
        """Shallow copy self."""
        obj = type(self).__new__(self.__class__)
        obj.__dict__.update(self.__dict__)
        return obj

    def append_child(self, item: Self):
        item.parent_item = self
        self.children.append(item)

    def insert_children(self, idx: int, items: Sequence[Self]):
        self.children[idx:idx] = items
        for item in items:
            item.parent_item = self

    def parent(self) -> Self | None:
        return self.parent_item

    @property
    def ancestors(self) -> Iterable[Self]:
        """Get iterator to yield all ancestors of self, does not include self."""
        node = self
        while (node := node.parent_item) is not None:
            yield node

    @property
    def descendants(self) -> Iterable[Self]:
        """Get iterator to yield all descendants of self, does not include self."""
        yield from preorder_iter(self, filter_condition=lambda _node: _node != self)

    @property
    def leaves(self) -> Iterable[Self]:
        """Get iterator to yield all leaf nodes from self."""
        yield from preorder_iter(self, filter_condition=lambda _node: _node.is_leaf)

    @property
    def siblings(self) -> Iterable[Self]:
        """Get siblings of self."""
        if self.parent_item is None:
            return ()
        return tuple(child for child in self.parent_item.children if child is not self)

    @property
    def left_sibling(self) -> Self | None:
        """Get sibling left of self."""
        if not self.parent_item:
            return None
        children = self.parent_item.children
        if child_idx := children.index(self):
            return self.parent_item.children[child_idx - 1]
        return None

    @property
    def right_sibling(self) -> Self | None:
        """Get sibling right of self."""
        if not self.parent_item:
            return None
        children = self.parent_item.children
        child_idx = children.index(self)
        if child_idx + 1 < len(children):
            return self.parent_item.children[child_idx + 1]
        return None

    @property
    def node_path(self) -> Iterable[Self]:
        """Get tuple of nodes starting from root."""
        if self.parent_item is None:
            return [self]
        return (*list(self.parent_item.node_path), self)

    @property
    def is_root(self) -> bool:
        """Get indicator if self is root node."""
        return self.parent_item is None

    @property
    def is_leaf(self) -> bool:
        """Get indicator if self is leaf node."""
        return not len(list(self.children))

    @property
    def root(self) -> Self:
        """Get root node of tree."""
        return self if self.parent_item is None else self.parent_item.root

    @property
    def depth(self) -> int:
        """Get depth of self, indexing starts from 1."""
        return 1 if self.parent_item is None else self.parent_item.depth + 1

    @property
    def max_depth(self) -> int:
        """Get maximum depth from root to leaf node."""
        return max(
            [self.root.depth] + [node.depth for node in list(self.root.descendants)]
        )

    def row(self) -> int:
        return self.parent_item.children.index(self) if self.parent_item else 0

    def pretty_print(self, indent: int = 0):
        text = indent * "    " + repr(self)
        logger.info(text)
        for child_item in self.children:
            child_item.pretty_print(indent + 1)


def preorder_iter(
    tree: BaseNode,
    filter_condition: Callable[[BaseNode], bool] | None = None,
    stop_condition: Callable[[BaseNode], bool] | None = None,
    max_depth: int = 0,
) -> Iterable[BaseNode]:
    """Iterate through all children of a tree.

    Pre-Order Iteration Algorithm, NLR
        1. Visit the current node.
        2. Recursively traverse the current node's left subtree.
        3. Recursively traverse the current node's right subtree.

    It is topologically sorted because a parent node is processed before its child nodes.

    >>> path_list = ["a/b/d", "a/b/e/g", "a/b/e/h", "a/c/f"]
    >>> root = list_to_tree(path_list)
    >>> print_tree(root)
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

    >>> [node.node_name for node in preorder_iter(root,
    filter_condition=lambda x: x.node_name in ["a", "d", "e", "f", "g"])]
    ['a', 'd', 'e', 'g', 'f']

    >>> [node.node_name for node in preorder_iter(root,
    stop_condition=lambda x: x.node_name=="e")]
    ['a', 'b', 'd', 'c', 'f']

    >>> [node.node_name for node in preorder_iter(root, max_depth=3)]
    ['a', 'b', 'd', 'e', 'c', 'f']

    Args:
        tree: input tree
        filter_condition: function that takes in node as argument, optional
            Return node if condition evaluates to `True`
        stop_condition: function that takes in node as argument, optional
            Stops iteration if condition evaluates to `True`
        max_depth: maximum depth of iteration, based on `depth` attribute, optional
    """
    if (
        tree
        and (not max_depth or tree.depth <= max_depth)
        and (not stop_condition or not stop_condition(tree))
    ):
        if not filter_condition or filter_condition(tree):
            yield tree
        for child in tree.children:
            yield from preorder_iter(child, filter_condition, stop_condition, max_depth)


if __name__ == "__main__":
    model = BaseNode()
    model.parent()

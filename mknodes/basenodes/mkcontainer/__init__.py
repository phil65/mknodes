from __future__ import annotations

from abc import abstractmethod
from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mknode
from mknodes.utils import log

if TYPE_CHECKING:
    from collections.abc import Iterator


logger = log.get_logger(__name__)


class MkContainerBase(mknode.MkNode):
    """Abstract base class for nodes containing other MkNodes.

    Subclasses must implement get_items() and set_items() methods.
    """

    ICON = "material/database"

    def __init__(
        self,
        *,
        block_separator: str = "\n\n",
        **kwargs: Any,
    ):
        """Constructor.

        Args:
            block_separator: Separator to put between blocks. Defaults to 2 linebreaks
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.block_separator = block_separator

    def __bool__(self):
        return bool(self.get_items())

    def __add__(self, other: str | mknode.MkNode):
        self.append(other)
        return self

    def __iter__(self) -> Iterator[mknode.MkNode]:  # type: ignore
        return iter(self.get_items())

    def _to_markdown(self) -> str:
        return self.block_separator.join(i.to_markdown() for i in self.get_items())

    @abstractmethod
    def get_items(self) -> list[mknode.MkNode]:
        """Return the list of contained items."""
        ...

    @abstractmethod
    def set_items(self, items: list[mknode.MkNode]) -> None:
        """Set the list of contained items."""
        ...

    # TODO: Remove items/children properties once templates are migrated to use
    # get_items()/get_children() methods. See metadata.toml files in node directories.
    @property
    def items(self) -> list[mknode.MkNode]:
        """Property for backward compatibility with templates."""
        return self.get_items()

    @items.setter
    def items(self, items: list[mknode.MkNode]) -> None:
        self.set_items(items)

    def get_children(self) -> list[mknode.MkNode]:  # type: ignore[override]
        """Return children - delegates to get_items for containers."""
        return self.get_items()

    def set_children(self, children: list[mknode.MkNode]) -> None:  # type: ignore[override]
        """Set children - delegates to set_items for containers."""
        self.set_items(children)

    def append(self, other: str | mknode.MkNode) -> None:
        """Append a MkNode to the end of this container.

        Args:
            other: The node / text to append
        """
        node = self.to_child_node(other)
        items = self.get_items()
        items.append(node)

    def insert(self, index: int, other: str | mknode.MkNode) -> None:
        """Insert a MkNode into desired position of this container.

        Args:
            index: Position where node should get inserted
            other: The node / text to insert
        """
        node = self.to_child_node(other)
        items = self.get_items()
        items.insert(index, node)


class MkContainer(MkContainerBase):
    """A node containing other MkNodes.

    This is the concrete implementation with list-based storage.
    Can be used directly or as a base class.
    Nodes added to a container are automatically re-parented.
    """

    def __init__(
        self,
        content: list[Any] | str | mknode.MkNode | None = None,
        *,
        block_separator: str = "\n\n",
        **kwargs: Any,
    ):
        """Constructor.

        Args:
            content: Child Nodes of this container
            block_separator: Separator to put between blocks. Defaults to 2 linebreaks
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(block_separator=block_separator, **kwargs)
        match content:
            case None:
                self._items: list[mknode.MkNode] = []
            case str():
                self._items = [self.to_child_node(content)] if content else []
            case mknode.MkNode():
                self._items = [self.to_child_node(content)]
            case list():
                self._items = [self.to_child_node(i) for i in content]
            case _:
                raise TypeError(content)

    def get_items(self) -> list[mknode.MkNode]:
        """Return the list of contained items."""
        return self._items

    def set_items(self, items: list[mknode.MkNode]) -> None:
        """Set the list of contained items."""
        self._items = items


if __name__ == "__main__":
    section = MkContainer()
    print(section)

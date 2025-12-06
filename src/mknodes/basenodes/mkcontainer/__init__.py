from __future__ import annotations

from abc import abstractmethod
from typing import Any, Self

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkContainerBase(mknode.MkNode):
    """Abstract base class for nodes containing other MkNodes.

    Subclasses must implement get_items() and set_items() methods.
    """

    ICON = "material/database"

    def __init__(self, *, block_separator: str = "\n\n", **kwargs: Any) -> None:
        """Constructor.

        Args:
            block_separator: Separator to put between blocks. Defaults to 2 linebreaks
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.block_separator = block_separator

    def __bool__(self) -> bool:
        return bool(self.get_items())

    def __add__(self, other: str | mknode.MkNode) -> Self:
        self.append(other)
        return self

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: collect markdown and resources from children."""
        items = self.get_items()

        # Collect content from all children in one pass
        child_contents = [await item.get_content() for item in items]

        # Aggregate child markdown - apply each child's processors
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        md = self.block_separator.join(child_markdowns)

        # Aggregate resources: own + all children
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    @abstractmethod
    def get_items(self) -> list[mknode.MkNode]:
        """Return the list of contained items."""
        ...

    @abstractmethod
    def set_items(self, items: list[mknode.MkNode]) -> None:
        """Set the list of contained items."""
        ...

    def get_children(self) -> list[mknode.MkNode]:
        """Return children - delegates to get_items for containers."""
        return self.get_items()

    def append(self, other: str | mknode.MkNode) -> None:
        """Append a MkNode to the end of this container.

        Args:
            other: The node / text to append
        """
        node = self.to_child_node(other)
        items = self.get_items()
        items.append(node)


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
    ) -> None:
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

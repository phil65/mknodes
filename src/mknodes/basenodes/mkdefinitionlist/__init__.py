from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TYPE_CHECKING
from jinja2 import filters
from mknodes.basenodes import mkcontainer
from mknodes.utils import log, reprhelpers, resources

if TYPE_CHECKING:
    from mknodes.basenodes import mknode


logger = log.get_logger(__name__)


class MkDefinition(mkcontainer.MkContainer):
    """Node for a single definition."""

    REQUIRED_EXTENSIONS = [resources.Extension("def_list")]
    ICON = "material/library"

    def __init__(
        self,
        content: list[Any] | str | mknode.MkNode | None = None,
        title: str = "",
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            content: Markdown content for this block
            title: Setting title
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.title = title

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with definition formatting and resources."""
        content = await super().get_content()
        md = f"{self.title}\n:   {filters.do_indent(content.markdown)}\n"
        return resources.NodeContent(markdown=md, resources=content.resources)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


class MkDefinitionList(mkcontainer.MkContainer):
    """Node for definition lists."""

    REQUIRED_EXTENSIONS = [resources.Extension("def_list")]
    ICON = "material/library"

    def __init__(self, data: Mapping[str, Any] | None = None, **kwargs: Any) -> None:
        """Constructor.

        Args:
            data: Data show for the table
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.data: dict[str, str | mknode.MkNode] = {}
        self.set_items(data)

    def __repr__(self) -> str:
        kws = {k: reprhelpers.to_str_if_textnode(v) for k, v in self.data.items()}
        return reprhelpers.get_repr(self, data=kws)

    def get_items(self) -> list[mknode.MkNode]:  # type: ignore[override]
        """Return the list of definition values."""
        return list(self.data.values())  # type: ignore[arg-type]

    def set_items(self, data: Mapping[str, Any] | list[Any] | None) -> None:
        """Set items from data."""
        match data:
            case Mapping():
                self.data = {k: self.to_child_node(v) for k, v in data.items()}
            case list():
                self.data = {str(i): self.to_child_node(item) for i, item in enumerate(data)}
            case None:
                self.data = {}
            case _:  # pyright: ignore[reportUnnecessaryComparison]
                raise TypeError(data)

    async def to_md_unprocessed(self) -> str:
        items = [f"{k}\n:   {filters.do_indent(str(v))}\n" for k, v in self.data.items()]
        return "".join(items)


if __name__ == "__main__":
    ls = MkDefinitionList(data=dict(a="b\nc", c="d"))
    print(ls)

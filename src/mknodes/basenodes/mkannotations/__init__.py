from __future__ import annotations as _annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from jinja2 import filters

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, reprhelpers, resources


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


class MkAnnotation(mkcontainer.MkContainer):
    """Represents a single annotation. It gets managed by an MkAnnotations node."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.superfences")]

    def __init__(self, num: int, content: str | mk.MkNode, **kwargs: Any) -> None:
        """Constructor.

        Args:
            num: Annotation index number
            content: Annotation content
            kwargs: Keyword arguments passed to parent
        """
        self.num = num
        super().__init__(content=content, **kwargs)

    def __repr__(self) -> str:
        return reprhelpers.get_repr(self, num=self.num, content=self.get_items())

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with annotation formatting and resources."""
        items = self.get_items()

        # Collect content from children
        child_contents = [await item.get_content() for item in items]

        # Build markdown with annotation formatting
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        item_str = "\n\n".join(child_markdowns)
        prefix = f"{self.num}."
        md = f"{prefix:<4}{filters.do_indent(item_str)}\n"

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


class MkAnnotations(mkcontainer.MkContainer):
    """Node containing a list of MkAnnotations."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.superfences")]
    ICON = "material/alert-box"

    def __init__(
        self,
        annotations: Mapping[int, str | mk.MkNode] | list[mk.MkNode | str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            annotations: Annotations data (Can be given in different shapes)
            kwargs: Keyword arguments passed to parent
        """
        match annotations:
            case None:
                items = []
            case list():
                items = [
                    (ann if isinstance(ann, MkAnnotation) else MkAnnotation(i, ann))
                    for i, ann in enumerate(annotations, start=1)
                ]
            case Mapping():
                items = [MkAnnotation(k, content=v) for k, v in annotations.items()]
            case _:  # pyright: ignore[reportUnnecessaryComparison]
                raise TypeError(annotations)
        super().__init__(content=items, **kwargs)

    def get_items(self) -> list[MkAnnotation]:  # type: ignore[override]
        """Return the list of annotations."""
        return self._items  # type: ignore[return-value]

    def __getitem__(self, item: int) -> MkAnnotation:
        for node in self.get_items():
            if node.num == item:
                return node
        raise IndexError(item)

    def __contains__(self, item: int | MkAnnotation) -> bool:
        match item:
            case MkAnnotation():
                return item in self.get_items()
            case int():
                return any(i.num == item for i in self.get_items())
            case _:
                raise TypeError(item)

    def __repr__(self) -> str:
        notes: list[str | MkAnnotation] = []
        for item in self.get_items():
            item_children = item.get_items()
            if len(item_children) == 1:
                string = reprhelpers.to_str_if_textnode(item_children[0])
                notes.append(string)
            else:
                notes.append(item)
        return reprhelpers.get_repr(self, annotations=notes)

    def _get_item_pos(self, num: int) -> int:
        items = self.get_items()
        item = next(i for i in items if i.num == num)
        return items.index(item)

    def __setitem__(self, index: int, value: mk.MkNode | str) -> None:
        import mknodes as mk

        match value:
            case str():
                item = mk.MkText(value)
                node = MkAnnotation(index, content=item, parent=self)
            case MkAnnotation():
                node = value
            case mk.MkNode():
                node = MkAnnotation(index, content=value, parent=self)
        items = self.get_items()
        if index in self:
            pos = self._get_item_pos(index)
            items[pos] = node
        else:
            items.append(node)

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content from sorted annotations and resources."""
        items = self.get_items()
        if not items:
            return resources.NodeContent(
                markdown="",
                resources=await self._build_node_resources(),
            )

        items = sorted(items, key=lambda x: x.num)

        # Collect content from children
        child_contents = [await item.get_content() for item in items]

        # Build markdown - children already formatted
        child_markdowns = []
        for item, child_content in zip(items, child_contents):
            md = child_content.markdown
            for proc in item.get_processors():
                md = proc.run(md)
            child_markdowns.append(md)

        md = "".join(child_markdowns)

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=md, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown

    def annotate_text(self, markdown: str) -> str:
        if not self.get_items():
            return markdown
        return f'<div class="annotate" markdown>\n{markdown}\n</div>\n\n{self}'


if __name__ == "__main__":
    import mknodes as mk

    page = mk.MkPage()
    print(page)

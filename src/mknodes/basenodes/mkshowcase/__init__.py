from __future__ import annotations

import textwrap

import tomllib
import os
from typing import TYPE_CHECKING, Any

from jinja2 import filters

from mknodes.basenodes import mkcard, mkcontainer
from mknodes.pages import mkpage
from mknodes.utils import log, pathhelpers, resources


if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    import mknodes as mk


logger = log.get_logger(__name__)


class MkShowcase(mkcontainer.MkContainer):
    """Node for showing a html-based image grid.

    Manages row / column positioning.
    Mainly intended for MkCards, but can also include other markdown (there are limits
    though.)
    When adding MkCards, then addtional CSS is required.
    """

    ICON = "material/view-grid"

    def __init__(
        self,
        items: list[str | mknode.MkNode] | None = None,
        *,
        column_count: int = 3,
        **kwargs: Any,
    ) -> None:
        self.column_count = column_count
        if isinstance(items, str | os.PathLike):
            text = pathhelpers.load_file_cached(str(items))
            data = tomllib.loads(text)
            items = [mkcard.MkCard(**dct) for dct in data.values()]
        elif isinstance(items, dict):
            items = [mkcard.MkCard(**dct) for dct in items.values()]
        super().__init__(content=items or [], **kwargs)

    def to_child_node(self, item) -> mknode.MkNode:
        match item:
            case mkpage.MkPage():
                return mkcard.MkCard(
                    target=item,
                    title=item.title or " ",
                    caption=item.subtitle or " ",
                    image=":material-tab:",
                    parent=self,
                )
            case mkcard.MkCard():
                return item
            case _:
                return super().to_child_node(item)

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with grid formatting and resources."""
        items = self.get_items()
        # Collect content from children
        child_contents = [await item.get_content() for item in items]
        # Build markdown with grid formatting
        text = ""
        content_iter = iter(zip(items, child_contents))
        for batch in filters.do_batch(items, self.column_count):
            text += '<div class="row">'
            for _ in batch:
                item, child_content = next(content_iter)
                # Apply child's processors
                md = child_content.markdown
                for proc in item.get_processors():
                    md = proc.run(md)
                text += '\n  <div class="column">\n'
                text += textwrap.indent(md, "    ")
                text += "  </div>"
            text += "\n</div>"

        # Aggregate resources
        aggregated = await self._build_node_resources()
        for child_content in child_contents:
            aggregated.merge(child_content.resources)

        return resources.NodeContent(markdown=text, resources=aggregated)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown

    def add_card(
        self,
        title: str,
        image: str,
        target: str | mk.MkPage | mk.MkNav | None = None,
        caption: str | None = None,
    ) -> None:
        """Add an image card to the node.

        Args:
            title: Card title
            image: link to the Image
            target: Optional link for the card
            caption: Image caption
        """
        card = mkcard.MkCard(target=target, title=title, image=image, caption=caption)
        self.append(card)


if __name__ == "__main__":
    import mknodes as mk

    keys = mk.MkKeys(keys="Ctrl+A")
    grid = MkShowcase()
    grid.add_card("Tse", "td", "http://www.google.com")
    print(grid.get_items()[0])

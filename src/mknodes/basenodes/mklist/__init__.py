from __future__ import annotations

from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mkcontainer
from mknodes.info import linkprovider
from mknodes.utils import log, resources

if TYPE_CHECKING:
    from mknodes.basenodes import mknode
    from collections.abc import Sequence


logger = log.get_logger(__name__)


class MkList(mkcontainer.MkContainer):
    """Node for showing a formatted list."""

    ICON = "octicons/list-unordered-24"
    REQUIRED_EXTENSIONS = [resources.Extension("def_list")]

    def __init__(
        self,
        items: Sequence[str | mknode.MkNode] | None = None,
        *,
        ordered: bool = False,
        shorten_after: int | None = None,
        as_links: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            items: Items to show as a list
            ordered: whether the list should be numbered
            shorten_after: will clip the list after n items and append a "..."
            as_links: will convert the label to links which will get replaced by plugin
            kwargs: Keyword arguments passed to parent
        """
        # if as_links:
        #     items = [link.Link(i) for i in items]
        items = items or []
        self.ordered = ordered
        self.shorten_after = shorten_after
        self.as_links = as_links
        super().__init__(content=list(items), **kwargs)

    def _prep(self, item: mknode.MkNode) -> str:
        return linkprovider.linked(str(item)) if self.as_links else str(item)

    async def to_md_unprocessed(self) -> str:
        items = self.get_items()
        if not items:
            return ""
        lines = [
            f"  {f'{i}.' if self.ordered else '*'} {self._prep(item)}"
            for i, item in enumerate(items[: self.shorten_after], start=1)
        ]
        if self.shorten_after and len(items) > self.shorten_after:
            prefix = f"{self.shorten_after + 1}." if self.ordered else "*"
            lines.append(f"  {prefix} ...")
        return "\n".join(lines) + "\n"

    async def to_html(self) -> str:
        """Formats list in html as one single line.

        Can be useful for including in Tables.
        """
        items = self.get_items()
        if not items:
            return ""
        tag_name = "ol" if self.ordered else "ul"
        li_items = [f"<li>{self._prep(i)}</li>" for i in items[: self.shorten_after]]
        item_str = "".join(li_items)
        if self.shorten_after and len(items) > self.shorten_after:
            item_str += "<li>...</li>"
        return f"<{tag_name}>{item_str}</{tag_name}>"


if __name__ == "__main__":
    section = MkList(["a", "b"])

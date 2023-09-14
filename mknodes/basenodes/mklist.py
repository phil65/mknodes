from __future__ import annotations

from collections.abc import Sequence

from mknodes.basenodes import mkcontainer, mknode
from mknodes.info import linkprovider
from mknodes.utils import helpers, log, reprhelpers


logger = log.get_logger(__name__)


class MkList(mkcontainer.MkContainer):
    """Node for showing a formatted list."""

    ICON = "octicons/list-unordered-24"
    REQUIRED_EXTENSIONS = ["def_list"]

    def __init__(
        self,
        items: Sequence[str | mknode.MkNode] | None = None,
        *,
        ordered: bool = False,
        shorten_after: int | None = None,
        as_links: bool = False,
        header: str = "",
    ):
        """Constructor.

        Arguments:
            items: Items to show as a list
            ordered: whether the list should be numbered
            shorten_after: will clip the list after n items and append a "..."
            as_links: will convert the label to links which will get replaced by plugin
            header: Section header
        """
        # if as_links:
        #     items = [link.Link(i) for i in items]
        items = items or []
        self.ordered = ordered
        self.shorten_after = shorten_after
        self.as_links = as_links
        super().__init__(content=list(items), header=header)

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        items = [helpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(
            self,
            items=items,
            shorten_after=self.shorten_after,
            as_links=self.as_links,
            _filter_empty=True,
            _filter_false=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        list_1 = MkList(items=["Item 1", "Item 2", "Item 3"])
        # list can also have a max length. they will get shortened with a "..." entry.
        list_2 = MkList(items=["Item"] * 6, shorten_after=3)
        # They can also be ordered.
        list_3 = MkList(items=["Item 1", "Item 2", "Item 3"], ordered=True)
        # and can contain markdown.
        list_4 = MkList(items=[mknodes.MkAdmonition("Markup")] * 3)

        page += mknodes.MkReprRawRendered(list_1, header="### Regular")
        page += mknodes.MkReprRawRendered(list_2, header="### Shortened")
        page += mknodes.MkReprRawRendered(list_3, header="### Ordered")
        page += mknodes.MkReprRawRendered(list_4, header="### Containing markdown")

    def _prep(self, item) -> str:
        return linkprovider.linked(str(item)) if self.as_links else str(item)

    def _to_markdown(self) -> str:
        if not self.items:
            return ""
        prefix = "1." if self.ordered else "*"
        lines = [f"  {prefix} {self._prep(i)}" for i in self.items[: self.shorten_after]]
        if self.shorten_after and len(self.items) > self.shorten_after:
            lines.append(f"  {prefix} ...")
        return "\n".join(lines) + "\n"

    def to_html(self) -> str:
        """Formats list in html as one single line.

        Can be useful for including in Tables.
        """
        if not self.items:
            return ""
        tag_name = "ol" if self.ordered else "ul"
        items = [f"<li>{self._prep(i)}</li>" for i in self.items[: self.shorten_after]]
        item_str = "".join(items)
        if self.shorten_after and len(self.items) > self.shorten_after:
            item_str += "<li>...</li>"
        return f"<{tag_name}>{item_str}</{tag_name}>"


if __name__ == "__main__":
    section = MkList(["a", "b"], header="test")
    print(section.to_html())

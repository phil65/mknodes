from __future__ import annotations

import logging

from mknodes import mkcontainer, mknode, utils


logger = logging.getLogger(__name__)


class MkList(mkcontainer.MkContainer):
    """Class to show a formatted list."""

    def __init__(
        self,
        items: list[str | mknode.MkNode] | None = None,
        *,
        shorten_after: int | None = None,
        as_links: bool = False,
        header: str = "",
    ):
        # if as_links:
        #     items = [link.Link(i) for i in items]
        super().__init__(items=items, header=header)
        self.shorten_after = shorten_after
        self.as_links = as_links

    def __str__(self):
        return self.to_markdown()

    def __len__(self):
        return len(self.items)

    def __repr__(self):
        return utils.get_repr(
            self,
            items=self.items,
            shorten_after=self.shorten_after,
            as_links=self.as_links,
        )

    @staticmethod
    def examples():
        yield dict(items=["Item 1", "Item 2", "Item 2"])
        yield dict(items=["Item"] * 6, shorten_after=3)

    def _prep(self, item):
        return utils.linked(item) if self.as_links else str(item)

    def _to_markdown(self) -> str:
        if not self.items:
            return ""
        lines = [f"  - {self._prep(i)}" for i in self.items[: self.shorten_after]]
        if self.shorten_after and len(self.items) > self.shorten_after:
            lines.append("  - ...")
        return "\n".join(lines) + "\n"

    def to_html(self) -> str:
        """Formats list in html as one single line.

        Can be useful for including in Tables.
        """
        if not self.items:
            return ""
        items = [f"<li>{self._prep(i)}</li>" for i in self.items[: self.shorten_after]]
        item_str = "".join(items)
        if self.shorten_after and len(self.items) > self.shorten_after:
            item_str += "<li>...</li>"
        return f"<ul>{item_str}</ul>"


if __name__ == "__main__":
    section = MkList(["a", "b"], header="test")
    print(section.to_html())

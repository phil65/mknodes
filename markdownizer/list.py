from __future__ import annotations

import logging

from markdownizer import markdownnode, utils


logger = logging.getLogger(__name__)


class List(markdownnode.MarkdownNode):
    """Class to show a formatted list."""

    def __init__(
        self,
        listitems: list[str] | None = None,
        shorten_after: int | None = None,
        header: str = "",
    ):
        super().__init__(header)
        self.listitems = listitems or []
        self.shorten_after = shorten_after

    def __str__(self):
        return self.to_markdown()

    def __len__(self):
        return len(self.listitems)

    def __repr__(self):
        return utils.get_repr(self, listitems=self.listitems)

    @staticmethod
    def examples():
        yield dict(listitems=["Item 1", "Item 2", "Item 2"])
        yield dict(listitems=["Item"] * 6, shorten_after=3)

    def _to_markdown(self):
        if not self.listitems:
            return ""
        lines = [f"  - {i}" for i in self.listitems[: self.shorten_after]]
        if self.shorten_after and len(self.listitems) > self.shorten_after:
            lines.append("  - ...")
        return "\n" + "\n".join(lines) + "\n"

    def to_html(self, make_link: bool = False):
        if not self.listitems:
            return ""
        item_str = "".join(
            f"<li>{utils.linked(i)}</li>" if make_link else f"<li>{i}</li>"
            for i in self.listitems[: self.shorten_after]
        )
        if self.shorten_after and len(self.listitems) > self.shorten_after:
            item_str += "<li>...</li>"
        return f"<ul>{item_str}</ul>"


if __name__ == "__main__":
    section = List(["a", "b"], header="test")
    print(section.to_markdown())

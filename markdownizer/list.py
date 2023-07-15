from __future__ import annotations

import logging

from markdownizer import basesection, utils


logger = logging.getLogger(__name__)


class List(basesection.MarkdownNode):
    def __init__(self, listitems: list[str] | None = None, header: str = ""):
        super().__init__(header)
        self.listitems = listitems

    def __str__(self):
        return self.to_markdown()

    def __len__(self):
        return len(self.listitems)

    def __repr__(self):
        return utils.get_repr(self, listitems=self.listitems)

    def _to_markdown(self):
        lines = [f"  - {i}" for i in self.listitems]
        return "\n" + "\n".join(lines) + "\n"

    def to_html(self, shorten_after: int | None = None, make_link: bool = False):
        if not self.listitems:
            return ""
        item_str = "".join(
            f"<li>{utils.linked(i)}</li>" if make_link else f"<li>{i}</li>"
            for i in self.listitems[:shorten_after]
        )
        if shorten_after and len(self.listitems) > shorten_after:
            item_str += "<li>...</li>"
        return f"<ul>{item_str}</ul>"


if __name__ == "__main__":
    section = List(["a", "b"], header="test")
    print(section.to_markdown())

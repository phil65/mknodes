from __future__ import annotations

import logging
import pathlib

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkImage(mknode.MkNode):
    """Image including optional caption."""

    def __init__(
        self,
        path: str,
        *,
        caption: str = "",
        title: str = "Image title",
        header: str = "",
    ):
        super().__init__(header=header)
        self.title = title
        self.caption = caption
        # TODO: linkreplacer doesnt work yet with full path
        self.path = pathlib.Path(path).name  # this should not be needed.

    def _to_markdown(self) -> str:
        lines = ["<figure markdown>", f"  ![{self.title}]({self.path})"]
        if self.caption:
            lines.append(f"  <figcaption>{self.caption}</figcaption>")
        lines.append("</figure>")
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    img = MkImage("Some path")

from __future__ import annotations

import logging
import textwrap

from mknodes import mkblock, mknode


logger = logging.getLogger(__name__)


class MkHtmlBlock(mkblock.MkBlock):
    """pymdownx-based block."""

    def __init__(
        self,
        content: str | mknode.MkNode = "",
        *,
        attributes: dict[str, str | bool] | None = None,
        **kwargs,
    ):
        super().__init__(typ="html", title="div", content=content)

    def _to_markdown(self) -> str:
        block_limiter = "///"
        lines = [f"{block_limiter} {self.typ} | {self.title}"]
        lines.extend(f"    {k}: {v}" for k, v in self.attributes.items())
        lines.append("")
        lines.extend(
            (textwrap.indent(str(self.content), "    ").rstrip("\n"), block_limiter),
        )
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    test = MkHtmlBlock("test")
    print(test)

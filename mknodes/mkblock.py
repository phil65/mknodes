from __future__ import annotations

import logging

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkBlock(mknode.MkNode):
    """pymdownx-based block."""

    def __init__(
        self,
        typ: str,
        content: str | mknode.MkNode = "",
        *,
        title: str = "",
        attributes: dict[str, str | bool] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.typ = typ
        self.attributes = attributes or {}
        self.title = title
        self.content = content

    def _to_markdown(self) -> str:
        block_limiter = "///"
        lines = [f"{block_limiter} {self.typ} | {self.title}"]
        lines.extend(f"    {k}: {v}" for k, v in self.attributes.items())
        lines.extend((str(self.content).rstrip("\n"), block_limiter))
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    test = MkBlock("tab", title="abc", content="bcd", attributes=dict(new=True))
    print(test)

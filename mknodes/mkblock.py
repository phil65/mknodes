from __future__ import annotations

import logging

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkBlock(mknode.MkNode):
    """pymdownx-based block."""

    def __init__(
        self,
        name: str,
        content: str | mknode.MkNode = "",
        *,
        argument: str = "",
        attributes: dict[str, str | bool] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.name = name
        self.attributes = attributes or {}
        self.argument = argument
        self.content = content

    def _to_markdown(self) -> str:
        block_limiter = "///"
        base = f"{block_limiter} {self.name}"
        if self.argument:
            base += f" | {self.argument}"
        lines = [base]
        lines.extend(f"    {k}: {v}" for k, v in self.attributes.items())
        lines.extend((str(self.content).rstrip("\n"), block_limiter))
        return "\n".join(lines) + "\n"


if __name__ == "__main__":
    test = MkBlock("tab", argument="abc", content="bcd", attributes=dict(new=True))
    print(test)

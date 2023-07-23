from __future__ import annotations

import logging

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkBlock(mknode.MkNode):
    """pymdownx-based block."""

    TYPE: str

    def __init__(
        self,
        content: str | mknode.MkNode = "",
        title: str = "",
        attributes: dict[str, str | bool] | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.attributes = attributes or {}
        self.title = title
        self.content = content

    def _to_markdown(self) -> str:
        lines = [f"/// {self.TYPE} | {self.title}"]
        lines.extend(f"    {k}: {v}" for k, v in self.attributes.items())
        lines.extend((str(self.content).rstrip("\n"), "///"))
        return "\n".join(lines) + "\n"


if __name__ == "__main__":

    class Test(MkBlock):
        TYPE = "Test"

    test = Test(title="abc", content="bcd", attributes=dict(new=True))
    print(test)

from __future__ import annotations

import logging

from typing import Any, Literal, get_args

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)

CriticMarkStr = Literal["addition", "deletion", "comment", "highlight"]


class MkCritic(mkcontainer.MkContainer):
    """MkCritic block."""

    ICON = "material/format-text"
    REQUIRED_EXTENSIONS = ["pymdownx.critic"]

    def __init__(
        self,
        content: str | mknode.MkNode | list,
        *,
        mark: CriticMarkStr = "highlight",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Content to mark
            mark: type of mark
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.mark = mark

    def __repr__(self):
        return reprhelpers.get_repr(self, content=self.items, mark=self.mark)

    def _to_markdown(self) -> str:
        match self.mark:
            case "addition":
                left, right = ("++", "++")
            case "deletion":
                left, right = ("--", "--")
            case "highlight":
                left, right = ("==", "==")
            case "comment":
                left, right = (">>", "<<")
            case _:
                raise TypeError(self.mark)
        return f"{{{left}\n\n{super()._to_markdown()}\n\n{right}}}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "The MkCritic node can be used to display text diffs."
        for typ in get_args(CriticMarkStr):
            node = MkCritic(f"This is type {typ}", mark=typ)
            page += mknodes.MkHeader(f"Type {typ!r}", level=3)
            page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    mkcritic = MkCritic("hello")
    print(mkcritic)

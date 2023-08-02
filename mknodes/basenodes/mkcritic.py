from __future__ import annotations

import logging

from typing import Any, Literal

from mknodes.basenodes import mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)

CriticMarkStr = Literal["addition", "deletion", "substitution", "comment", "highlight"]


class MkCritic(mktext.MkText):
    """MkCritic block."""

    ICON = "material/format-text"
    REQUIRED_EXTENSIONS = ["pymdownx.critic"]

    def __init__(
        self,
        text: str,
        *,
        mark: CriticMarkStr = "addition",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            text: Critic text
            mark: type of Critic
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(text=text, **kwargs)
        self.mark = mark

    def __repr__(self):
        return helpers.get_repr(self, text=self.text, mark=self.mark)

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
        return f"{{{left}\n\n{self.text}\n\n{right}}}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "The MkCritic node can be used to display text diffs."
        for typ in ["addition", "deletion", "comment", "highlight"]:
            node = MkCritic(mark=typ, text=f"This is type {typ}")
            page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    mkcritic = MkCritic("hello")
    print(mkcritic)

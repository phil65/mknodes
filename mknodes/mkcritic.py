from __future__ import annotations

import logging

from typing import Literal

from mknodes import mktext


logger = logging.getLogger(__name__)

CriticMarkStr = Literal["addition", "deletion", "substitution", "comment", "highlight"]


class MkCritic(mktext.MkText):
    """MkCritic block."""

    def __init__(
        self,
        text: str,
        mark: CriticMarkStr = "addition",
        **kwargs,
    ):
        super().__init__(text=text, **kwargs)
        self.mark = mark

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
    def examples():
        for typ in ["addition", "deletion", "comment", "highlight"]:
            yield dict(mark=typ, text=f"This is type {typ}")


if __name__ == "__main__":
    mkcritic = MkCritic("hello")
    print(mkcritic)

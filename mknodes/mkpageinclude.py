from __future__ import annotations

import logging
import os
import pathlib

from typing import Literal

from mknodes import mknode, mkpage


logger = logging.getLogger(__name__)

CriticMarkStr = Literal["addition", "deletion", "substitution", "comment", "highlight"]


class MkPageInclude(mknode.MkNode):
    """MkCritic block."""

    def __init__(
        self,
        page: str | os.PathLike | mkpage.MkPage,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.page = page

    def _to_markdown(self) -> str:
        match self.page:
            case os.PathLike() | str():
                left, right = "{%", "%}"
                text = pathlib.Path(self.page).read_text()
                return f"{{{left}\n\n{text}\n\n{right}}}"
            case mkpage.MkPage():
                return str(self.page)
            case _:
                raise TypeError(self.page)

    @staticmethod
    def examples():
        yield dict(page=mkpage.MkPage(items=["test"]))


if __name__ == "__main__":
    mkcritic = MkPageInclude(page=mkpage.MkPage(items=["test"]))
    print(mkcritic)

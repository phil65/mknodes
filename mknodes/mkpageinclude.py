from __future__ import annotations

import logging
import os
import pathlib

from typing import Any

from mknodes import mknode, mkpage


logger = logging.getLogger(__name__)


class MkPageInclude(mknode.MkNode):
    """Node to include other MkPages / Md files."""

    def __init__(
        self,
        page: str | os.PathLike | mkpage.MkPage,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            page: page to include
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.page = page

    def _to_markdown(self) -> str:
        match self.page:
            # case os.PathLike() | str():
            #     left, right = "{%", "%}"
            #     text = pathlib.Path(self.page).read_text()
            #     return f"{left}\n\n{text}\n\n{right}"
            case os.PathLike() | str():
                return pathlib.Path(self.page).read_text()
            case mkpage.MkPage():
                return str(self.page)
            case _:
                raise TypeError(self.page)


if __name__ == "__main__":
    page = mkpage.MkPage(content="test")
    include = MkPageInclude(page=__file__)
    print(include)

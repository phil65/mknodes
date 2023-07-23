from __future__ import annotations

import logging
import os

from mknodes import mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkSnippet(mknode.MkNode):
    """Snippet to include markdown from another file.

    [More info](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)
    """

    REQUIRED_EXTENSIONS = "pymdownx.snippets"

    def __init__(self, path: str | os.PathLike, header: str = ""):
        super().__init__(header)
        self.path = path

    def __str__(self):
        return self.to_markdown()

    def __repr__(self):
        return helpers.get_repr(self, path=str(self.path))

    def _to_markdown(self) -> str:
        return f"--8<--\n{self.path}\n--8<--\n"


if __name__ == "__main__":
    section = MkSnippet("test.md", header="test")
    print(section.to_markdown())

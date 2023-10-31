from __future__ import annotations

import os
from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkSnippet(mknode.MkNode):
    """Snippet to include markdown from another file.

    [More info](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)
    """

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.snippets")]
    ICON = "material/paperclip"

    def __init__(self, path: str | os.PathLike, **kwargs: Any):
        """Constructor.

        Arguments:
            path: Path to markdown file
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.path = path

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        node = MkSnippet(path="README.md")
        page += mk.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        return f"--8<--\n{self.path}\n--8<--\n"


if __name__ == "__main__":
    section = MkSnippet("test.md", header="test")
    print(section.to_markdown())

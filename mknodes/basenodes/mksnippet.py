from __future__ import annotations

import os

from mknodes.basenodes import mknode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


class MkSnippet(mknode.MkNode):
    """Snippet to include markdown from another file.

    [More info](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)
    """

    REQUIRED_EXTENSIONS = ["pymdownx.snippets"]
    ICON = "material/paperclip"

    def __init__(
        self,
        path: str | os.PathLike,
        *,
        header: str = "",
    ):
        """Constructor.

        Arguments:
            path: Path to markdown file.
            header: Section header
        """
        super().__init__(header=header)
        self.path = path

    def __str__(self):
        return self.to_markdown()

    def __repr__(self):
        return reprhelpers.get_repr(self, path=str(self.path))

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkSnippet(path="README.md")
        page += mknodes.MkReprRawRendered(node)

    def _to_markdown(self) -> str:
        return f"--8<--\n{self.path}\n--8<--\n"


if __name__ == "__main__":
    section = MkSnippet("test.md", header="test")
    print(section.to_markdown())

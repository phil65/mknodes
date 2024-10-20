from __future__ import annotations

from typing import Any, TYPE_CHECKING

from mknodes.basenodes import mknode
from mknodes.utils import log, resources

if TYPE_CHECKING:
    import os


logger = log.get_logger(__name__)


class MkSnippet(mknode.MkNode):
    """Snippet to include markdown from another file.

    [More info](https://facelessuser.github.io/pymdown-extensions/extensions/snippets/)
    """

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.snippets")]
    ICON = "material/paperclip"

    def __init__(self, path: str | os.PathLike[str], **kwargs: Any):
        """Constructor.

        Arguments:
            path: Path to markdown file
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.path = path

    def _to_markdown(self) -> str:
        return f"--8<--\n{self.path}\n--8<--\n"


if __name__ == "__main__":
    section = MkSnippet("test.md")
    print(section.to_markdown())

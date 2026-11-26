import os

from typing import Any
from urllib import parse

from mknodes import inputs
from mknodes.basenodes import mktext
from mknodes.pages import mkpage
from mknodes.utils import log, pathhelpers


logger = log.get_logger(__name__)


class MkInclude(mktext.MkText):
    """Node to include the text of other Markdown files / MkNodes.

    This node only keeps a reference to given target and resolves it when needed.
    Target can either be an URL or any other fsspec protocol path to a markdown file,
    a file system path to a markdown file, or another MkNode.
    """

    ICON = "octicons/file-symlink-file-24"

    def __init__(self, target: str | os.PathLike[str] | mktext.MkText, **kwargs: Any) -> None:
        """Constructor.

        Args:
            target: target to include
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.target = target

    def _remote_url(self) -> str | None:
        """Return the target if it is an http(s) URL (pinned in the lock file)."""
        if isinstance(self.target, str) and parse.urlsplit(self.target).scheme in {
            "http",
            "https",
        }:
            return self.target
        return None

    def get_input_requests(self) -> list[inputs.InputRequest]:
        if url := self._remote_url():
            return [inputs.InputRequest.create("file", url=url)]
        return []

    async def get_text(self) -> str:
        if url := self._remote_url():
            return await self.ctx.inputs.aget("file", url=url)
        match self.target:
            case os.PathLike() | str():
                return pathhelpers.load_file_cached(os.fspath(self.target))
            case mktext.MkText():
                return str(self.target)
            case _:
                raise TypeError(self.target)


if __name__ == "__main__":
    page = mkpage.MkPage(content="test")
    url = "https://raw.githubusercontent.com/phil65/mknodes/main/README.md"
    include = MkInclude(target=url)
    print(include)

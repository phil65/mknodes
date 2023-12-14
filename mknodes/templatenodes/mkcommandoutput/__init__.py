from __future__ import annotations


from typing import Any, TYPE_CHECKING

from mknodes.templatenodes import mktemplate
from mknodes.utils import log, resources

if TYPE_CHECKING:
    from collections.abc import Sequence


logger = log.get_logger(__name__)


class MkCommandOutput(mktemplate.MkTemplate):
    """Node to display the terminal output of a command."""

    ICON = "material/bash"
    STATUS = "new"
    CSS = [resources.CSSFile("terminal.css")]

    def __init__(self, call: Sequence[str], **kwargs: Any):
        """Constructor.

        Arguments:
            call: System call to make
            kwargs: Keyword arguments passed to parent
        """
        self.call = call
        super().__init__("output/html/template", **kwargs)

    @property
    def cwd(self):
        return self.ctx.metadata.repository_path


if __name__ == "__main__":
    text = MkCommandOutput.with_context(["dir"])
    print(text)

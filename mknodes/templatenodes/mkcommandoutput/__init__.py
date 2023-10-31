from __future__ import annotations

from collections.abc import Sequence
import os

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import helpers, log, resources


logger = log.get_logger(__name__)


TEXT = """<div data-terminal>
  <span data-ty="input">{input}</span>
  <span data-ty>{output}</span>
</div>"""


class MkCommandOutput(mknode.MkNode):
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
        # caching on instance level as a compromise
        self._cache: dict[str, str] = {}  # {call: output}
        super().__init__(**kwargs)

    @property
    def output(self) -> str:
        import pathlib

        key = " ".join(self.call)
        if key in self._cache:
            return self._cache[key]
        cwd = self.ctx.metadata.repository_path or pathlib.Path.cwd()
        if output := helpers.get_output_from_call(key, cwd=cwd):
            self._cache[key] = output  # .replace("\n", "<br>").replace(" ", "&nbsp;")
            return self._cache[key]
        return "**Command failed**"

    def _to_markdown(self):
        call = " ".join(self.call)
        return TEXT.format(input=call, output=self.output)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        if os.environ.get("CI"):
            node = MkCommandOutput(["make", "help"])
            node = mk.MkReprRawRendered(node)
        else:
            node = mk.MkHeader("Sadly breaks log output ATM, so only triggered in CI")
        page += node


if __name__ == "__main__":
    text = MkCommandOutput.with_context(["dir"])
    print(text)

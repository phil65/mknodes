from __future__ import annotations

from collections.abc import Sequence
import os

from mknodes.basenodes import mknode
from mknodes.utils import helpers, log, reprhelpers


logger = log.get_logger(__name__)


TEXT = """<div data-terminal>
  <span data-ty="input">{input}</span>
  <span data-ty>{output}</span>
</div>"""


class MkCommandOutput(mknode.MkNode):
    """Node to display the terminal output of a command."""

    ICON = "material/bash"
    STATUS = "new"
    CSS = "css/terminal.css"

    def __init__(self, call: Sequence[str], **kwargs):
        self.call = call
        # caching on instance level as a compromise
        self._cache: dict[str, str] = {}  # {call: output}
        super().__init__(**kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, call=self.call)

    @property
    def output(self):
        key = " ".join(self.call)
        if key in self._cache:
            return self._cache[key]
        if output := helpers.get_output_from_call(self.call):
            self._cache[key] = output  # .replace("\n", "<br>").replace(" ", "&nbsp;")
            return self._cache[key]
        return "**Command failed**"

    def _to_markdown(self):
        call = " ".join(self.call)
        return TEXT.format(input=call, output=self.output)

    @staticmethod
    def create_example_page(page):
        import mknodes

        if os.environ.get("CI"):
            node = MkCommandOutput(["make", "help"])
            node = mknodes.MkReprRawRendered(node)
        else:
            node = mknodes.MkHeader(
                "Sadly breaks log output ATM, so only triggered in CI",
            )
        page += node


if __name__ == "__main__":
    text = MkCommandOutput(["make", "help"])
    print(text)

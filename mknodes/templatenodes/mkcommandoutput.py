from __future__ import annotations

from collections.abc import Sequence
import logging

from mknodes.basenodes import mknode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


TEXT = """<div data-terminal>
  <span data-ty="input">{input}</span>
  <span data-ty>{output}</span>
</div>"""


def get_output_from_call(call: Sequence[str]):
    import subprocess

    try:
        return subprocess.check_output(call).decode()
    except subprocess.CalledProcessError:
        logger.warning("Executing %s failed", call)
        return None


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
        if output := get_output_from_call(self.call):
            self._cache[key] = output.replace("\n", "<br>").replace(" ", "&nbsp;")
            return self._cache[key]
        return "**Command failed**"

    def _to_markdown(self):
        call = " ".join(self.call)
        return TEXT.format(input=call, output=self.output)

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkCommandOutput(["make", "help"])
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    text = MkCommandOutput(["make", "help"])
    print(text)

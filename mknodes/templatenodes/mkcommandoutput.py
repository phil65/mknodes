from __future__ import annotations

from collections.abc import Sequence
import logging

from mknodes.basenodes import mkcode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkCommandOutput(mkcode.MkCode):
    """Node to display the terminal output of a command."""

    ICON = "material/bash"
    STATUS = "new"

    def __init__(self, call: Sequence[str], **kwargs):
        self.call = call
        # caching on instance level as a compromise
        self._cache: dict[str, str] = {}  # {call: output}
        super().__init__(language="", **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, call=self.call)

    @property
    def text(self):
        key = " ".join(self.call)
        if key in self._cache:
            return self._cache[key]
        if output := helpers.get_output_from_call(self.call):
            self._cache[key] = output
            return self._cache[key]
        return "**Command failed**"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkCommandOutput(["make", "help"])
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    text = MkCommandOutput(["make", "help"])
    print(text)

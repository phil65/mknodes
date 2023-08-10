from __future__ import annotations

from collections.abc import Sequence
import logging
import subprocess

from mknodes.basenodes import mkcode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkSystemCall(mkcode.MkCode):
    """Table showing info dependencies for a package."""

    ICON = "material/database"

    def __init__(self, call: Sequence[str], **kwargs):
        self.call = call
        super().__init__(**kwargs)

    def __repr__(self):
        return helpers.get_repr(self, call=self.call)

    @property
    def text(self):
        return subprocess.check_output(["make", "help"]).decode()

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.status = "new"
        node = MkSystemCall(["make", "help"])
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    text = MkSystemCall(["make", "help"])
    print(text)

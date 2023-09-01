from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkKeys(mknode.MkNode):
    """Node to include other MkPages / Md files."""

    REQUIRED_EXTENSIONS = ["pymdownx.keys"]
    ICON = "fontawesome/regular/keyboard"

    def __init__(
        self,
        keys: str | list[str],
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            keys: keys to display
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        match keys:
            case str():
                self.keys = keys.lower().split("+")
            case list():
                self.keys = [i.lower() for i in keys]

    def __repr__(self):
        return reprhelpers.get_repr(self, keys=self.keys)

    def _to_markdown(self) -> str:
        key_str = "+".join(self.keys)
        return f"++{key_str}++"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += mknodes.MkAdmonition("MkKeys can be used to show Key combinations.")
        page += mknodes.MkReprRawRendered(MkKeys("M+k+K+e+y+s"))
        page += mknodes.MkReprRawRendered(MkKeys("Ctrl+A"))


if __name__ == "__main__":
    keys = MkKeys(keys="Ctrl+A")
    print(keys)

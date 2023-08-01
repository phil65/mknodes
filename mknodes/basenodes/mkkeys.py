from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mknode


logger = logging.getLogger(__name__)


class MkKeys(mknode.MkNode):
    """Node to include other MkPages / Md files."""

    REQUIRED_EXTENSIONS = ["pymdownx.keys"]

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

    def _to_markdown(self) -> str:
        key_str = "+".join(self.keys)
        return f"++{key_str}++"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page.metadata["status"] = "new"
        page += mknodes.MkAdmonition("MkKeys can be used to show Key combinations.")
        node = MkKeys("Ctrl+A")
        page += node
        page += mknodes.MkCode(str(node), header="Markdown")


if __name__ == "__main__":
    keys = MkKeys(keys="Ctrl+A")
    print(keys)

from __future__ import annotations

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkKeys(mknode.MkNode):
    """Node to display Keyboard keys.

    Mostly used to explain shortcuts / commands for the keyboard.
    """

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.keys")]
    ICON = "fontawesome/regular/keyboard"
    ATTR_LIST_SEPARATOR = ""

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


if __name__ == "__main__":
    keys = MkKeys(keys="Ctrl+A")

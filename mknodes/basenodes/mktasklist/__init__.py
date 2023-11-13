from __future__ import annotations

from typing import Any

from jinja2 import filters

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTask(mkcontainer.MkContainer):
    """Node for a single task listitem."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.tasklist")]
    ICON = "material/library"

    def __init__(
        self,
        value: bool = False,
        content: list | None | str | mknode.MkNode = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            value: Setting value
            content: Markdown content for this block
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.value = value

    def _to_markdown(self) -> str:
        text = super()._to_markdown()
        val = "x" if self.value else " "
        return f"- [{val}] {filters.do_indent(str(text))}\n"


class MkTaskList(mkcontainer.MkContainer):
    """Node for task lists."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.tasklist")]
    ICON = "material/library"

    def __init__(
        self,
        content: list | None | str | mknode.MkNode = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: Data show for the table
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, block_separator="", **kwargs)

    def add_item(self, content, value):
        item = MkTask(value, content)
        self.append(item)


if __name__ == "__main__":
    ls = MkTaskList()
    ls.add_item("True", True)
    ls.add_item("False", False)
    print(ls)

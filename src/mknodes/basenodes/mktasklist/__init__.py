from __future__ import annotations

from typing import Any, TYPE_CHECKING

from jinja2 import filters

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, resources

if TYPE_CHECKING:
    from mknodes.basenodes import mknode


logger = log.get_logger(__name__)


class MkTask(mkcontainer.MkContainer):
    """Node for a single task listitem."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.tasklist")]
    ICON = "material/library"

    def __init__(
        self,
        value: bool = False,
        content: list | str | mknode.MkNode | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            value: Setting value
            content: Markdown content for this block
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, **kwargs)
        self.value = value

    async def get_content(self) -> resources.NodeContent:
        """Single-pass: get content with task formatting and resources."""
        content = await super().get_content()
        val = "x" if self.value else " "
        md = f"- [{val}] {filters.do_indent(content.markdown)}\n"
        return resources.NodeContent(markdown=md, resources=content.resources)

    async def to_md_unprocessed(self) -> str:
        content = await self.get_content()
        return content.markdown


class MkTaskList(mkcontainer.MkContainer):
    """Node for task lists."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.tasklist")]
    ICON = "material/library"

    def __init__(
        self,
        content: list | str | mknode.MkNode | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            content: Data show for the table
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(content=content, block_separator="", **kwargs)

    def add_item(self, content, value: bool) -> None:
        item = MkTask(value, content)
        self.append(item)


if __name__ == "__main__":
    ls = MkTaskList()
    ls.add_item("True", True)
    ls.add_item("False", False)
    print(ls)

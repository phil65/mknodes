from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mkblock, mknode
from mknodes.utils import helpers, log, reprhelpers


logger = log.get_logger(__name__)


MarkdownModeStr = Literal["block", "inline", "raw", "auto", "html"]

RawBlockTags = Literal["pre", "canvas", "math", "option"]
RawHtmlTags = Literal["script", "style"]
BlockTypeStr = Literal["div", "span", "code"] | RawHtmlTags | RawBlockTags


class MkHtmlBlock(mkblock.MkBlock):
    """PyMdown-based Html block. Can be used to show raw content."""

    ICON = "octicons/code-16"
    REQUIRED_EXTENSIONS = ["pymdownx.blocks.html"]

    def __init__(
        self,
        content: str | mknode.MkNode = "",
        *,
        block_type: BlockTypeStr = "div",
        markdown_mode: MarkdownModeStr | None = None,
        attributes: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            content: What should be contained in the block
            block_type: Block type
            markdown_mode: Markdown mode
            attributes: Block attrs
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            name="html",
            argument=block_type,
            content=content,
            attributes=attributes,
            **kwargs,
        )
        self.markdown_mode = markdown_mode
        self.indent = "    "

    def __repr__(self):
        if len(self.items) == 1:
            content = helpers.to_str_if_textnode(self.items[0])
        else:
            content = [helpers.to_str_if_textnode(i) for i in self.items]
        return reprhelpers.get_repr(
            self,
            content=content,
            block_type=self.argument,
            markdown_mode=self.markdown_mode,
            attributes=self.attributes,
            _filter_empty=True,
        )

    @property
    def markdown_mode(self) -> MarkdownModeStr | None:
        """The markdown mode attribute."""
        return self.attributes.get("markdown")

    @markdown_mode.setter
    def markdown_mode(self, value: MarkdownModeStr | None):
        self.attributes["markdown"] = value


if __name__ == "__main__":
    test = MkHtmlBlock("test")
    print(test)

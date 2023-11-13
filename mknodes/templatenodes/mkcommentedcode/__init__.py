from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mkcontainer, mknode
from mknodes.data import datatypes
from mknodes.utils import inspecthelpers, log


logger = log.get_logger(__name__)


class MkCommentedCode(mkcontainer.MkContainer):
    """Node which displays a list of code / comment blocks for given code.

    Lines beginning with # are shown in dedicated blocks and can be used to
    inline-explain the code. Lines can be hidden by ending a line with "##".
    """

    ICON = "material/code-json"
    STATUS = "new"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        code: str | datatypes.HasCodeType,
        language: str = "py",
        *,
        linenums: int | None = None,
        style: Literal["text", "admonition", "bubble"] = "bubble",
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            code: Code to show
            language: language for syntax highlighting
            linenums: If set, use as start linenumber
            style: Comment style
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        self._code = code
        self.language = language
        self.title = ""
        self.linenums = linenums
        self._style = style
        super().__init__(content=None, header=header, **kwargs)

    @property
    def code(self) -> str:
        match self._code:
            case str():
                return self._code
            case _:
                return inspecthelpers.get_source(self._code)

    @property
    def comment_class(self) -> type[mknode.MkNode]:
        import mknodes as mk

        match self._style:
            case "text":
                return mk.MkText
            case "bubble":
                return mk.MkSpeechBubble
            case "admonition":
                return mk.MkAdmonition
            case _:
                raise TypeError(self._style)

    @property
    def items(self):
        import mknodes as mk

        items = []
        for sec in inspecthelpers.iter_code_sections(self.code, self.linenums):
            if sec.typ == "code":
                items += mk.MkCode(sec.code, linenums=sec.start_line, parent=self)
            else:
                items += self.comment_class(sec.code, parent=self)
        return items

    @items.setter
    def items(self, value):
        pass

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # Comment sections automatically get converted to non-codeblock sections.
        # That way you can explain your code in-line.

        # ## you can use headers.

        node = MkCommentedCode(MkCommentedCode.create_example_page)
        page += mk.MkReprRawRendered(node, header="### Regular")
        # !!! note
        #     Admonitions and everything else work, too.
        #

        node = MkCommentedCode(MkCommentedCode.create_example_page, style="admonition")
        page += mk.MkReprRawRendered(node, header="### Admonitions")
        node = MkCommentedCode(MkCommentedCode.create_example_page, style="text")
        page += mk.MkReprRawRendered(node, header="### Plain text")


if __name__ == "__main__":
    from mknodes.manual import root

    node = MkCommentedCode(root.build)
    print(node)

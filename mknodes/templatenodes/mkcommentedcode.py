from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import (
    mkadmonition,
    mkcode,
    mkcontainer,
    mknode,
    mkspeechbubble,
    mktext,
)
from mknodes.data import datatypes
from mknodes.utils import inspecthelpers, log, reprhelpers


logger = log.get_logger(__name__)


class MkCommentedCode(mkcontainer.MkContainer):
    """Node which displays a list of code / comment blocks for given code.

    Lines beginning with # are shown in dedicated blocks and can be used to
    inline-explain the code. Lines can be hidden by ending a line with "#".
    """

    ICON = "material/code-json"
    STATUS = "new"

    REQUIRED_EXTENSIONS = [
        "pymdownx.highlight",
        "pymdownx.snippets",
        "pymdownx.superfences",
    ]

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

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            code=self._code,
            language=self.language,
            linenums=self.linenums,
            style=self._style,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def code(self):
        match self._code:
            case str():
                return self._code
            case _:
                return inspecthelpers.get_source(self._code)

    @property
    def comment_class(self):
        match self._style:
            case "text":
                return mktext.MkText
            case "bubble":
                return mkspeechbubble.MkSpeechBubble
            case "admonition":
                return mkadmonition.MkAdmonition
            case _:
                raise TypeError(self._style)

    @property
    def items(self):
        if not self.code:
            return {}
        section: list[str] = []
        sections: list[mknode.MkNode] = []
        mode = ""
        line_num = self.linenums or 0
        for i, line in enumerate(self.code.split("\n"), start=line_num):
            if not line.strip() or line.rstrip().endswith("##"):
                continue
            if line.strip().startswith("#"):
                if mode == "code":
                    code = "\n".join(section)
                    start_line = line_num if self.linenums else None
                    sections.append(mkcode.MkCode(code, linenums=start_line))
                    section = []
                    line_num = i
                section.append(line.strip().removeprefix("#")[1:])
                mode = "comment"
            elif not line.strip().startswith("#"):
                if mode == "comment":
                    text = "\n".join(section)
                    sections.append(self.comment_class(text))
                    section = []
                    line_num = i
                section.append(line)
                mode = "code"
        if mode == "code":
            code = "\n".join(section)
            start_line = line_num if self.linenums else None
            sections.append(mkcode.MkCode(code, linenums=start_line))
        elif mode == "comment":
            text = "\n".join(section)
            sections.append(self.comment_class(text))
        for sect in sections:
            sect.parent = self
        return sections

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        import mknodes

        # Comment sections automatically get converted to non-codeblock sections.
        # That way you can explain your code in-line.

        # ## you can use headers.

        node = MkCommentedCode(MkCommentedCode.create_example_page)
        page += mknodes.MkReprRawRendered(node, header="### Regular")
        # !!! note
        #     Admonitions and everything else work, too.
        #

        node = MkCommentedCode(MkCommentedCode.create_example_page, style="admonition")
        page += mknodes.MkReprRawRendered(node, header="### Admonitions")
        node = MkCommentedCode(MkCommentedCode.create_example_page, style="text")
        page += mknodes.MkReprRawRendered(node, header="### Plain text")


if __name__ == "__main__":
    from mknodes import manual

    node = MkCommentedCode(manual.build)
    print(node)

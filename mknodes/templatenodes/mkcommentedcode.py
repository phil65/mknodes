from __future__ import annotations

import logging

from typing import Any

from mknodes.basenodes import mkadmonition, mkcode, mkcontainer, mktext
from mknodes.data import datatypes
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


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
        use_admonitions: bool = False,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            code: Code to show
            language: language for syntax highlighting
            linenums: If set, use as start linenumber
            use_admonitions: If set, put comments into admonitions
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        self._code = code
        self.language = language
        self.title = ""
        self.linenums = linenums
        self.use_admonitions = use_admonitions
        super().__init__(content=None, header=header, **kwargs)

    def __repr__(self):
        return helpers.get_repr(
            self,
            code=self.code,
            language=self.language,
            linenums=self.linenums,
            use_admonitions=self.use_admonitions,
            _filter_empty=True,
            _filter_false=True,
        )

    @property
    def code(self):
        match self._code:
            case str():
                return self._code
            case _:
                return helpers.get_source(self._code)

    @property
    def items(self):
        if not self.code:
            return {}
        section = []
        sections = []
        mode = ""
        Class = (  # noqa: N806
            mkadmonition.MkAdmonition if self.use_admonitions else mktext.MkText
        )
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
                    sections.append(Class(text))
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
            sections.append(Class(text))
        for section in sections:
            section.parent = self
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

        node = MkCommentedCode(MkCommentedCode.create_example_page, use_admonitions=True)
        page += mknodes.MkReprRawRendered(node, header="### Admonitions")


if __name__ == "__main__":
    from mknodes import manual

    node = MkCommentedCode(manual.build)
    print(node)

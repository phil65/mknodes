from __future__ import annotations

from typing import Any, Literal, TYPE_CHECKING

from mknodes.templatenodes import mktemplate
from mknodes.utils import inspecthelpers, log

if TYPE_CHECKING:
    from mknodes.data import datatypes


logger = log.get_logger(__name__)


class MkCommentedCode(mktemplate.MkTemplate):
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
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            code: Code to show
            language: language for syntax highlighting
            linenums: If set, use as start linenumber
            style: Comment style
            kwargs: Keyword arguments passed to parent
        """
        self._code = code
        self.language = language
        self.title = ""
        self.linenums = linenums
        self.style = style
        super().__init__(template="output/markdown/template", **kwargs)

    @property
    def code(self) -> str:
        match self._code:
            case str():
                return self._code
            case _:
                return inspecthelpers.get_source(self._code)

    @classmethod
    def create_example_page(cls, page):
        # Comment sections automatically get converted to non-codeblock sections.
        # That way you can explain your code in-line.

        # ## you can use headers.

        page += MkCommentedCode(MkCommentedCode.create_example_page)
        # !!! note
        #     Admonitions and everything else work, too.
        #
        page += MkCommentedCode(MkCommentedCode.create_example_page, style="admonition")


if __name__ == "__main__":
    from mknodes.manual import get_started_section

    node = MkCommentedCode(get_started_section.a_quick_tour)
    print(node)

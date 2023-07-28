from __future__ import annotations

from collections.abc import Callable
import inspect
import logging
import textwrap
import types

from typing import Any

from typing_extensions import Self

from mknodes import mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkCode(mktext.MkText):
    """Class representing a Code block."""

    REQUIRED_EXTENSIONS = [
        "pymdownx.highlight",
        "pymdownx.inlinehilite",
        "pymdownx.snippets",
        "pymdownx.superfences",
    ]

    def __init__(
        self,
        code: str | mknode.MkNode = "",
        language: str = "py",
        *,
        title: str = "",
        header: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        parent=None,
    ):
        if isinstance(code, MkCode):
            code = textwrap.indent(str(code), "    ")
        super().__init__(code, header=header, parent=parent)
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines

    def _to_markdown(self) -> str:
        title = f" title={self.title!r}" if self.title else ""
        if self.highlight_lines:
            title += ' hl_lines="' + " ".join(str(i) for i in self.highlight_lines) + '"'
        return f"``` {self.language}{title}\n{self.text}\n```"

    @staticmethod
    def create_example_page(page):
        page += "A MkCode node can be used to display a code section"
        page += MkCode(language="python", code="a = 1 + 2")
        page += "You can also apply syntax highlighting for different languages"
        page += MkCode(language="js", code="var z = x + y;", title="JavaScript")
        page += "Highlighting lines is also possible"
        page += MkCode(code="1\n2\n3\n4", highlight_lines=[1, 3])

    @classmethod
    def for_object(
        cls,
        obj: types.ModuleType
        | type
        | types.MethodType
        | types.FunctionType
        | types.TracebackType
        | types.FrameType
        | types.CodeType
        | Callable[..., Any],
        *,
        dedent: bool = True,
        extract_body: bool = False,
        title: str | None = None,
        header: str = "",
    ) -> Self:
        if extract_body and isinstance(obj, type | types.FunctionType | types.MethodType):
            code = helpers.get_function_body(obj)
        elif extract_body:
            msg = "Can only extract body from Functions, Methods and classes"
            raise TypeError(msg)
        else:
            code = inspect.getsource(obj)
        code = textwrap.dedent(code) if dedent else code
        if title is not None:
            code_title = title
        elif isinstance(obj, types.TracebackType | types.FrameType | types.CodeType):
            code_title = ""
        else:
            code_title = obj.__name__
        return cls(code=code, header=header, title=code_title)


if __name__ == "__main__":
    code = MkCode.for_object(MkCode, extract_body=True)
    print(code)

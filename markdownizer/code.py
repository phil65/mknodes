from __future__ import annotations

import inspect
import itertools
import logging
import textwrap
import types

from typing_extensions import Self

from markdownizer import markdownnode


logger = logging.getLogger(__name__)


def get_function_body(func: types.MethodType | types.FunctionType | type) -> str:
    # see https://stackoverflow.com/questions/38050649
    source_lines = inspect.getsourcelines(func)[0]
    source_lines = itertools.dropwhile(lambda x: x.startswith("@"), source_lines)
    line = next(source_lines).strip()  # type: ignore
    if not line.startswith(("def ", "class ")):
        return line.rsplit(":")[-1].strip()
    elif not line.endswith(":"):
        for line in source_lines:
            line = line.strip()
            if line.endswith(":"):
                break
    return "".join(source_lines)


class Code(markdownnode.Text):
    """Class representing a Code block."""

    REQUIRED_EXTENSIONS = [
        "pymdownx.highlight",
        "pymdownx.inlinehilite",
        "pymdownx.snippets",
        "pymdownx.superfences",
    ]

    def __init__(
        self,
        language: str,
        code: str | markdownnode.MarkdownNode = "",
        *,
        title: str = "",
        header: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        parent=None,
    ):
        if isinstance(code, Code):
            code = textwrap.indent(str(code), "    ")
        super().__init__(code, header=header, parent=parent)
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines

    def _to_markdown(self) -> str:
        title = f" title={self.title!r}" if self.title else ""
        return f"``` {self.language}{title}\n{self.text}\n```"

    @staticmethod
    def examples():
        yield dict(language="python", code="a = 1 + 2")
        yield dict(language="js", code="var z = x + y;", title="JavaScript")

    @classmethod
    def for_object(
        cls,
        obj: types.ModuleType
        | type
        | types.MethodType
        | types.FunctionType
        | types.TracebackType
        | types.FrameType
        | types.CodeType,
        *,
        dedent: bool = True,
        extract_body: bool = False,
        header: str = "",
    ) -> Self:
        if extract_body and isinstance(obj, type | types.FunctionType | types.MethodType):
            code = get_function_body(obj)
        elif extract_body:
            raise TypeError("Can only extract body from Functions, Methods and classes")
        else:
            code = inspect.getsource(obj)
        code = textwrap.dedent(code) if dedent else code
        return cls(language="py", code=code, header=header)


if __name__ == "__main__":
    code = Code.for_object(Code, extract_body=True)
    print(code)

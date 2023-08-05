from __future__ import annotations

from collections.abc import Callable
import inspect
import logging
import os
import pathlib
import textwrap
import types

from typing import Any

from typing_extensions import Self

from mknodes.basenodes import mkcontainer, mknode
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkCode(mkcontainer.MkContainer):
    """Class representing a Code block."""

    ICON = "material/code-json"

    REQUIRED_EXTENSIONS = [
        "pymdownx.highlight",
        "pymdownx.snippets",
        "pymdownx.superfences",
    ]

    def __init__(
        self,
        code: str | mknode.MkNode | list = "",
        language: str = "py",
        *,
        title: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            code: Code to show
            language: language for syntax highlighting
            title: Code block title
            linenums: If set, use as start linenumber
            highlight_lines: Optionally highlight lines
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines
        super().__init__(content=code, header=header, **kwargs)

    def __repr__(self):
        return helpers.get_repr(
            self,
            code=self.items,
            language=self.language,
            title=self.title,
            linenums=self.linenums,
            highlight_lines=self.highlight_lines,
            _filter_empty=True,
        )

    @property
    def text(self):
        return "\n".join(str(i) for i in self.items)

    def _to_markdown(self) -> str:
        block_level = sum(isinstance(i, MkCode) for i in self.ancestors)
        block_limiter = "`" * (block_level + 3)
        title = f" title={self.title!r}" if self.title else ""
        if self.linenums is not None:
            title += f' linenums="{self.linenums}"'
        if self.highlight_lines:
            title += ' hl_lines="' + " ".join(str(i) for i in self.highlight_lines) + '"'
        return f"{block_limiter} {self.language}{title}\n{self.text}\n{block_limiter}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "A MkCode node can be used to display a code section"
        node_1 = MkCode(language="python", code="a = 1 + 2")
        page += mknodes.MkReprRawRendered(node_1, indent=True)
        page += "You can also apply syntax highlighting for different languages"
        node_2 = MkCode(language="js", code="var z = x + y;", title="syntax highlight")
        page += mknodes.MkReprRawRendered(node_2, indent=True)
        page += "Highlighting lines is also possible"
        node_3 = MkCode(code="1\n2\n3\n4", highlight_lines=[1, 3])
        page += mknodes.MkReprRawRendered(node_3, indent=True)
        page += "As well as numnbering the lines."
        node_4 = MkCode(code="1\n2\n3\n4", linenums=10)
        page += mknodes.MkReprRawRendered(node_4, indent=True)

    @classmethod
    def for_file(
        cls,
        path: str | os.PathLike,
        *,
        linenums: bool = True,
        highlight_caller: bool = True,
        title: str | None = None,
        **kwargs: Any,
    ):
        """Create a MkCode node based on a code file.

        Line numbers will be shown by default. If highlight_caller is True,
        it will try to detect whether the calling method is inside the code block are
        creating and if yes, it will highlight that line.

        Arguments:
            path: Path to the code file
            linenums: Whether to show line numbers
            highlight_caller: Whether we want to try to highlight the line which called
                              this method.
            title: title to use for the code box. If None is set, filename will be used.
            kwargs: Keyword arguments passed to MkCode ctor
        """
        path = pathlib.Path(path)
        with path.open() as file:
            content = file.read()
        hl_lines = None
        if highlight_caller and (frame := inspect.currentframe()) and frame.f_back:
            call_file = frame.f_back.f_code.co_filename
            if call_file == str(path.absolute()):
                line_count = content.count("\n")
                line = frame.f_back.f_lineno
                hl_lines = [line] if 0 <= line <= line_count else None
        start_line = 1 if linenums else None
        title = path.name if title is None else title
        return cls(
            content,
            linenums=start_line,
            title=title,
            highlight_lines=hl_lines,
            **kwargs,
        )

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
        linenums: bool = True,
        highlight_caller: bool = True,
        **kwargs: Any,
    ) -> Self:
        """Create a MkCode node based on a python object.

        Fetches code by using the inspect module.
        Line numbers will be shown by default. If highlight_caller is True,
        it will try to detect whether the calling method is inside the code block are
        displaying and if yes, it will highlight that line.

        Arguments:
            obj: Python object to show code from
            dedent: Whether to dedent the code
            extract_body: if True, Function / Class signatures are stripped from the code
            title: Title to use for code block. If None, it will use the object path.
            linenums: Whether to show line numbers
            highlight_caller: Whether we want to try to highlight the line which called
                              this method.
            kwargs: Keyword arguments passed to MkCode ctor
        """
        if extract_body and isinstance(obj, type | types.FunctionType | types.MethodType):
            code = helpers.get_function_body(obj)
        elif extract_body:
            msg = "Can only extract body from Functions, Methods and classes"
            raise TypeError(msg)
        else:
            code = inspect.getsource(obj)
        code = textwrap.dedent(code) if dedent else code
        match obj:
            case _ if title is not None:
                code_title = title
            case types.TracebackType() | types.FrameType() | types.CodeType():
                code_title = ""
            case Callable():
                code_title = classhelpers.to_dotted_path(obj)
            case _:
                code_title = obj.__name__
        hl_lines = None
        if linenums:
            lines, start_line = inspect.getsourcelines(obj)
            if highlight_caller and (frame := inspect.currentframe()) and frame.f_back:
                call_file = frame.f_back.f_code.co_filename
                obj_file = inspect.getfile(obj)
                if call_file == obj_file:
                    line_no = frame.f_back.f_lineno
                    line = line_no - start_line + 1
                    hl_lines = [line] if 0 <= line <= start_line + len(lines) else None
        else:
            start_line = None
        return cls(
            code=code,
            title=code_title,
            linenums=start_line,
            highlight_lines=hl_lines,
            **kwargs,
        )


if __name__ == "__main__":
    code = MkCode.for_object(MkCode, extract_body=True)
    code2 = MkCode(code)
    print(code2)

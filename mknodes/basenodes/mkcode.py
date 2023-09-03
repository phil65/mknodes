from __future__ import annotations

from collections.abc import Callable
import inspect
import logging
import os
import pathlib
import textwrap
import types

from typing import Any, Self

from mknodes.basenodes import mkcontainer, mknode
from mknodes.data import datatypes
from mknodes.utils import classhelpers, inspecthelpers, reprhelpers


logger = logging.getLogger(__name__)


class MkCode(mkcontainer.MkContainer):
    """Class representing a Code block."""

    ICON = "material/code-json"
    REQUIRED_EXTENSIONS = {
        "pymdownx.highlight": dict(
            anchor_linenums=True,
            line_spans="__span",
            pygments_lang_class=True,
        ),
        "pymdownx.snippets": {},
        "pymdownx.superfences": {},
    }

    def __init__(
        self,
        code: str | mknode.MkNode | list = "",
        language: str = "py",
        *,
        title: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        fence_level: int | None = None,
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
            fence_level: Determines amount of ` used for fence. If None, auto-determine.
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines
        self._fence_level = fence_level
        super().__init__(content=code, header=header, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            code=self.items,
            language=self.language,
            title=self.title,
            linenums=self.linenums,
            highlight_lines=self.highlight_lines,
            _filter_empty=True,
        )

    @property
    def text(self) -> str:
        """Text content."""
        return "\n".join(str(i) for i in self.items)

    @property
    def fence_boundary(self) -> str:
        """Fence boundary."""
        if self._fence_level:
            return "`" * (self._fence_level + 3)
        block_level = sum(isinstance(i, MkCode) for i in self.ancestors)
        return "`" * (block_level + 3)

    @property
    def fence_title(self) -> str:
        """Title in first line."""
        title = f" title={self.title!r}" if self.title else ""
        if self.linenums is not None:
            title += f' linenums="{self.linenums}"'
        if self.highlight_lines:
            title += ' hl_lines="' + " ".join(str(i) for i in self.highlight_lines) + '"'
        return f"{self.language}{title}"

    def _to_markdown(self) -> str:
        first_line = f"{self.fence_boundary} {self.fence_title}"
        return f"{first_line}\n{self.text}\n{self.fence_boundary}"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += mknodes.MkHeader("Regular", level=3)
        node_1 = MkCode(language="python", code="a = 1 + 2")
        page += mknodes.MkReprRawRendered(node_1)

        page += mknodes.MkHeader("Syntax highlighting", level=3)
        node_2 = MkCode(language="js", code="var z = x + y;", title="syntax highlight")
        page += mknodes.MkReprRawRendered(node_2)

        page += mknodes.MkHeader("Highlighting lines", level=3)
        node_3 = MkCode(code="1\n2\n3\n4", highlight_lines=[1, 3])
        page += mknodes.MkReprRawRendered(node_3)

        page += mknodes.MkHeader("Numbered lines", level=3)
        node_4 = MkCode(code="1\n2\n3\n4", linenums=10)
        page += mknodes.MkReprRawRendered(node_4)

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
        obj: datatypes.HasCodeType,
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
        if extract_body and callable(obj):
            code = inspecthelpers.get_function_body(obj)
        elif extract_body:
            msg = "Can only extract body from Functions, Methods and classes"
            raise TypeError(msg)
        else:
            code = inspecthelpers.get_source(obj)
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
        lines, start_line = inspecthelpers.get_source_lines(obj)
        if isinstance(obj, types.ModuleType):
            start_line += 1
        if highlight_caller and (frame := inspect.currentframe()) and frame.f_back:
            call_file = frame.f_back.f_code.co_filename
            obj_file = inspect.getfile(obj)
            if call_file == obj_file:
                line_no = frame.f_back.f_lineno
                line = line_no - start_line + 1
                hl_lines = [line] if 0 <= line <= start_line + len(lines) else None
        return cls(
            code=code,
            title=code_title,
            linenums=start_line if linenums else None,
            highlight_lines=hl_lines,
            **kwargs,
        )


if __name__ == "__main__":
    code = MkCode.for_object(MkCode, extract_body=True)
    code2 = MkCode(code)
    print(code2)

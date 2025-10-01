from __future__ import annotations

import inspect
import textwrap
import types

from jinjarope import textfilters
from typing import TYPE_CHECKING, Any, Self

from upathtools import to_upath

from mknodes.basenodes import mkcontainer
from mknodes.data import datatypes
from mknodes.utils import classhelpers, inspecthelpers, log, resources


if TYPE_CHECKING:
    import os
    import mknodes as mk

logger = log.get_logger(__name__)


class MkCode(mkcontainer.MkContainer):
    """Class representing a Code block."""

    ICON = "material/code-json"
    ATTR_LIST_SEPARATOR = "\n"
    REQUIRED_EXTENSIONS = [
        resources.Extension(
            "pymdownx.highlight",
            anchor_linenums=True,
            line_spans="__span",
            pygments_lang_class=True,
        ),
        resources.Extension("pymdownx.superfences"),
    ]

    def __init__(
        self,
        content: str | mk.MkNode | list = "",
        *,
        language: str = "python",
        title: str = "",
        linenums: int | None = None,
        highlight_lines: list[int] | None = None,
        fence_level: int | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Args:
            content: Content to show inside code box
            language: language for syntax highlighting
            title: Code block title
            linenums: If set, use as start linenumber
            highlight_lines: Optionally highlight lines
            fence_level: Determines amount of ticks used for fence.
                         If None, auto-determine based on nesting depth.
            kwargs: Keyword arguments passed to parent
        """
        self.language = language
        self.title = title
        self.linenums = linenums
        self.highlight_lines = highlight_lines
        self._fence_level = fence_level
        super().__init__(content=content, **kwargs)

    @property
    def text(self) -> str:
        """Text content."""
        return "\n".join(str(i) for i in self.items)

    @property
    def fence_boundary(self) -> str:
        """Return fence boundary, based on nesting level. Default is ```."""
        if self._fence_level:
            return "`" * (self._fence_level + 3)
        block_level = sum(isinstance(i, MkCode) for i in self.ancestors)
        return "`" * (block_level + 3)

    @property
    def fence_title(self) -> str:
        """Title in first line."""
        classes = " ".join(f".{i}" for i in self.mods.css_classes)
        attrs = {}
        if self.title:
            attrs["title"] = self.title
        if self.language:
            classes = f".{self.language} {classes}"
        if self.linenums is not None:
            attrs["linenums"] = str(self.linenums)
        if self.highlight_lines:
            sub = " ".join(str(i) for i in self.highlight_lines)
            attrs["hl_lines"] = sub
        if not classes and not attrs:
            return ""
        attr_str = " ".join(f"{k}={v!r}" for k, v in attrs.items())
        if attr_str:
            attr_str = " " + attr_str
        return f"{{{classes}{attr_str}}}"

    def _to_markdown(self) -> str:
        space = " " if self.fence_title else ""
        first_line = f"{self.fence_boundary}{space}{self.fence_title}"
        return f"{first_line}\n{self.text}\n{self.fence_boundary}"

    @classmethod
    def for_file(
        cls,
        path: str | os.PathLike[str],
        *,
        linenums: bool = True,
        highlight_caller: bool = True,
        title: str | None = None,
        language: str | None = None,
        **kwargs: Any,
    ):
        """Create a MkCode node based on a code file.

        Line numbers will be shown by default. If `highlight_caller` is `True`,
        it will try to detect whether the calling method is inside the code block are
        creating and if yes, it will highlight that line.

        Args:
            path: Path to the code file (also supports fsspec-protocol URLs)
            linenums: Whether to show line numbers
            highlight_caller: Whether we want to try to highlight the line which called
                              this method.
            title: title to use for the code box. If None is set, filename will be used.
            language: Syntax highlighting language. If None, try to infer from extension.
            kwargs: Keyword arguments passed to MkCode ctor
        """
        file_path = to_upath(path)
        content = file_path.read_text("utf-8")
        hl_lines = None
        if highlight_caller and (frame := inspect.currentframe()) and frame.f_back:
            call_file = frame.f_back.f_code.co_filename
            if call_file == str(file_path.absolute()):
                line_count = content.count("\n")
                line = frame.f_back.f_lineno
                hl_lines = [line] if 0 <= line <= line_count else None
        start_line = 1 if linenums else None
        title = file_path.name if title is None else title
        if language is None:
            language = datatypes.EXT_TO_PYGMENTS_STYLE.get(file_path.suffix, "")
        return cls(
            content,
            linenums=start_line,
            title=title,
            highlight_lines=hl_lines,
            language=language,
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

        Args:
            obj: Python object to show code from
            dedent: Whether to dedent the code
            extract_body: if True, Function / Class signatures are stripped from the code
            title: Title to use for code block. If None, it will use the object path.
            linenums: Whether to show line numbers
            highlight_caller: Whether we want to try to highlight the line which called
                              this method.
            kwargs: Keyword arguments passed to MkCode ctor
        """
        code = inspecthelpers.get_source(obj)
        if extract_body:
            if not callable(obj):
                msg = "Can only extract body from Functions, Methods and classes"
                raise TypeError(msg)
            code = textfilters.extract_body(code)
        code = textwrap.dedent(code) if dedent else code
        code_title = title if title is not None else classhelpers.get_code_name(obj)
        hl_lines = None
        lines, start_line = inspecthelpers.get_source_lines(obj)
        if isinstance(obj, types.ModuleType):
            start_line += 1
        if highlight_caller and (frame := inspect.currentframe()) and frame.f_back:
            call_file = frame.f_back.f_code.co_filename
            obj_file = inspecthelpers.get_file(obj)
            if call_file == obj_file:
                line_no = frame.f_back.f_lineno
                line = line_no - start_line + 1
                hl_lines = [line] if 0 <= line <= start_line + len(lines) else None
        return cls(
            code,
            title=code_title,
            linenums=start_line if linenums else None,
            highlight_lines=hl_lines,
            **kwargs,
        )


if __name__ == "__main__":
    code = MkCode.for_object(MkCode, extract_body=True)
    code2 = MkCode(code)
    print(code2)

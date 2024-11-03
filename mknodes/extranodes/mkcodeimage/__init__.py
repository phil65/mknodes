from __future__ import annotations

import textwrap

from typing import Any, Self, TYPE_CHECKING
import functools
from jinjarope import textfilters
import upath

from mknodes.basenodes import mknode
from mknodes.utils import classhelpers, inspecthelpers, log
import os

if TYPE_CHECKING:
    from mknodes.data import datatypes


logger = log.get_logger(__name__)


@functools.cache
def get_svg_for_code(
    text: str,
    title: str = "",
    width: int = 80,
    language: str = "py",
    pygments_style: str = "material",
) -> str:
    from rich.console import Console
    from rich.padding import Padding
    from rich.syntax import Syntax

    # with console.capture() as _capture:
    with open(os.devnull, "w") as devnull:  # noqa: PTH123
        console = Console(record=True, width=width, file=devnull, markup=False)
        syntax = Syntax(text, lexer=language, theme=pygments_style)
        renderable = Padding(syntax, (0,), expand=False)
        console.print(renderable, markup=False)
    return console.export_svg(title=title)


class MkCodeImage(mknode.MkNode):
    """Node to display a code block as an SVG image."""

    ICON = "material/code-json"

    def __init__(
        self,
        code: str | datatypes.HasCodeType = "",
        language: str = "py",
        *,
        title: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Args:
            code: Code to show
            language: language for syntax highlighting
            title: Code block title
            kwargs: Keyword arguments passed to parent
        """
        self.language = language
        self.title = title
        self._code = code
        super().__init__(**kwargs)

    @property
    def code(self) -> str:
        match self._code:
            case str():
                return self._code
            case _:
                return inspecthelpers.get_source(self._code)

    def _to_markdown(self) -> str:
        content = get_svg_for_code(
            self.code,
            language=self.language,
            title=self.title,
        )
        return f"<body>\n\n{content}\n\n</body>\n"

    @classmethod
    def for_file(
        cls,
        path: str | os.PathLike[str],
        *,
        storage_options: dict | None = None,
        title: str | None = None,
        **kwargs: Any,
    ):
        """Create a MkCode node based on a code file.

        Args:
            path: Path to the code file (also takes fsspec protocol URLs)
            storage_options: Options for fsspec backend
            title: title to use for the code box. If None is set, filename will be used.
            kwargs: Keyword arguments passed to MkCode ctor
        """
        opts = storage_options or {}
        file = upath.UPath(path, **opts)
        content = file.read_text("utf-8")
        title = file.name if title is None else title
        return cls(content, title=title, **kwargs)

    @classmethod
    def for_object(
        cls,
        obj: datatypes.HasCodeType,
        *,
        dedent: bool = True,
        extract_body: bool = False,
        title: str | None = None,
        **kwargs: Any,
    ) -> Self:
        """Create a MkCode node based on a python object.

        Fetches code by using the inspect module.

        Args:
            obj: Python object to show code from
            dedent: Whether to dedent the code
            extract_body: if True, Function / Class signatures are stripped from the code
            title: Title to use for code block. If None, it will use the object path.
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
        return cls(code, title=code_title, **kwargs)


if __name__ == "__main__":
    node = MkCodeImage.for_file("https://docs.python.org/index.html")
    print(node)

from __future__ import annotations

import os
import textwrap

from typing import Any, Self

import upath

from mknodes.basenodes import mknode
from mknodes.data import datatypes
from mknodes.utils import classhelpers, inspecthelpers, log, richhelpers


logger = log.get_logger(__name__)


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

        Arguments:
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
        content = richhelpers.get_svg_for_code(
            self.code,
            language=self.language,
            title=self.title,
        )
        return f"<body>\n\n{content}\n\n</body>\n"

    @classmethod
    def create_example_page(cls, page):
        node = MkCodeImage("a = 1 + 2", language="py", title="Window title")
        page += node

    @classmethod
    def for_file(
        cls,
        path: str | os.PathLike,
        *,
        storage_options: dict | None = None,
        title: str | None = None,
        **kwargs: Any,
    ):
        """Create a MkCode node based on a code file.

        Arguments:
            path: Path to the code file (also takes fsspec protocol URLs)
            storage_options: Options for fsspec backend
            title: title to use for the code box. If None is set, filename will be used.
            kwargs: Keyword arguments passed to MkCode ctor
        """
        opts = storage_options or {}
        file = upath.UPath(path, **opts)
        content = file.read_text()
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

        Arguments:
            obj: Python object to show code from
            dedent: Whether to dedent the code
            extract_body: if True, Function / Class signatures are stripped from the code
            title: Title to use for code block. If None, it will use the object path.
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
        code_title = title if title is not None else classhelpers.get_code_name(obj)
        return cls(code, title=code_title, **kwargs)


if __name__ == "__main__":
    node = MkCodeImage.for_file("https://docs.python.org/index.html")
    print(node)

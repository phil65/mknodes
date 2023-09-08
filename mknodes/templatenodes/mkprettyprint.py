from __future__ import annotations

import collections

from collections.abc import ItemsView, KeysView, ValuesView
import pprint
from types import MappingProxyType, SimpleNamespace
from typing import Any, ClassVar, Protocol, runtime_checkable

from mknodes.basenodes import mkcode
from mknodes.utils import log, reprhelpers


logger = log.get_logger(__name__)


@runtime_checkable
class IsDataclass(Protocol):
    __dataclass_fields__: ClassVar[dict]


class MkPrettyPrint(mkcode.MkCode):
    """Node to show a prettyprinted data structure."""

    ICON = "material/printer"

    def __init__(
        self,
        obj: dict
        | list
        | str
        | tuple
        | set
        | bytes
        | bytearray
        | MappingProxyType
        | SimpleNamespace
        | ValuesView
        | KeysView
        | collections.Counter
        | collections.ChainMap
        | collections.deque
        | collections.UserDict
        | collections.UserList
        | collections.UserString
        | ItemsView
        | IsDataclass,
        *,
        indent: int = 1,
        depth: int | None = None,
        width: int = 80,
        compact: bool = False,
        sort_dicts: bool = False,
        underscore_numbers: bool = False,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            obj: Object to prettyprint
            header: Section header
            indent: Specifies the amount of indentation added for each nesting level
            depth: Maximum nesting depth to print
            width: Specifies the desired maximum number of characters per line
            compact: Compact format for long sequences
            sort_dicts: Whether dicts should be sorted after keys
            underscore_numbers: Whether to use underscore as a separator for long numbers
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header, **kwargs)
        self.obj = obj
        self.print_indent = indent  # avoid name conflicts
        self.print_width = width
        self.print_depth = depth
        self.print_compact = compact
        self.print_sort_dicts = sort_dicts
        self.print_underscore_numbers = underscore_numbers

    @property
    def text(self):
        return pprint.pformat(
            self.obj,
            indent=self.print_indent,
            width=self.print_width,
            depth=self.print_depth,
            compact=self.print_compact,
            sort_dicts=self.print_sort_dicts,
            underscore_numbers=self.print_underscore_numbers,
        )

    @text.setter
    def text(self, text):
        self.obj = text

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            obj=self.obj,
            indent=self.print_indent,
            width=self.print_width,
            depth=self.print_depth,
            compact=self.print_compact,
            sort_dicts=self.print_sort_dicts,
            underscore_numbers=self.print_underscore_numbers,
            _filter_empty=True,
            _filter_false=True,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        node = MkPrettyPrint(obj=[dict(a="test " * 5)] * 5)
        page += mknodes.MkReprRawRendered(node)


if __name__ == "__main__":
    section = MkPrettyPrint([dict(a="test " * 5)] * 5, header="test")
    print(section.to_markdown())

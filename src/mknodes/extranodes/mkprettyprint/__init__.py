from __future__ import annotations

from typing import Any

import collections
from collections.abc import ItemsView, KeysView, ValuesView
from types import MappingProxyType, SimpleNamespace


from mknodes.data.datatypes import DataclassInstance
from mknodes.templatenodes import mktemplate
from mknodes.utils import log


logger = log.get_logger(__name__)


PrettyPrintableType = (
    dict[str, Any]
    | list[Any]
    | str
    | tuple[Any, ...]
    | set[Any]
    | bytes
    | bytearray
    | MappingProxyType[str, Any]
    | SimpleNamespace
    | ValuesView[Any]
    | KeysView[Any]
    | collections.Counter[Any]
    | collections.ChainMap[Any, Any]
    | collections.deque[Any]
    | collections.UserDict[Any, Any]
    | collections.UserList[Any]
    | collections.UserString
    | ItemsView[str, Any]
    | DataclassInstance
)


class MkPrettyPrint(mktemplate.MkTemplate):
    """Node to show a prettyprinted data structure."""

    ICON = "material/printer"

    def __init__(
        self,
        obj: PrettyPrintableType,
        *,
        nest_indent: int = 1,
        maximum_depth: int | None = None,
        char_width: int = 80,
        compact: bool = False,
        sort_dicts: bool = False,
        underscore_numbers: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            obj: Object to prettyprint
            nest_indent: Specifies the amount of indentation added for each nesting level
            maximum_depth: Maximum nesting depth to print
            char_width: Specifies the desired maximum number of characters per line
            compact: Compact format for long sequences
            sort_dicts: Whether dicts should be sorted after keys
            underscore_numbers: Whether to use underscore as a separator for long numbers
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/markdown/template", **kwargs)
        self.obj = obj
        self.nest_indent = nest_indent  # indent already used by MkNode
        self.char_width = char_width
        self.maximum_depth = maximum_depth  # depth / max_depth already used by Node
        self.compact = compact
        self.sort_dicts = sort_dicts
        self.underscore_numbers = underscore_numbers


if __name__ == "__main__":
    section = MkPrettyPrint([dict(a="test " * 5)] * 5)
    print(section.to_markdown())

from __future__ import annotations

import collections

from collections.abc import Callable, ItemsView, KeysView, ValuesView
from dataclasses import Field
import types
from types import MappingProxyType, SimpleNamespace
from typing import Any, ClassVar, Literal, Protocol, runtime_checkable


AdmonitionTypeStr = Literal[
    "note",
    "abstract",
    "info",
    "tip",
    "success",
    "question",
    "warning",
    "failure",
    "danger",
    "bug",
    "example",
    "quote",
]

ClassifierStr = Literal[
    "Development Status",
    "Environment",
    "Framework",
    "Intended Audience",
    "License",
    "Natural Language",
    "Operating System",
    "Programming Language",
    "Topic",
    "Typing",
]

CLASSIFIERS: list[ClassifierStr] = [
    "Development Status",
    "Environment",
    "Framework",
    "Intended Audience",
    "License",
    "Natural Language",
    "Operating System",
    "Programming Language",
    "Topic",
    "Typing",
]

EXT_TO_PYGMENTS_STYLE = {
    ".py": "py",
    ".yml": "yaml",
    ".yaml": "yaml",
    ".toml": "toml",
    ".md": "md",
    ".jinja": "jinja",
}

MetadataTypeStr = (
    Literal[
        "classifiers",
        "keywords",
        "keywords_combined",
        "websites",
        "dependencies",
        "required_python",
        "installed_packages",
    ]
    | ClassifierStr
)


@runtime_checkable
class DataclassInstance(Protocol):
    __dataclass_fields__: ClassVar[dict[str, Field[Any]]]


PrettyPrintableType = (
    dict
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
    | DataclassInstance
)


PageStatusStr = Literal["new", "deprecated", "encrypted"]

RGBColorType = tuple[int, int, int] | str
RGBAColorType = tuple[int, int, int, float] | str
ColorType = RGBColorType | RGBAColorType
HasCodeType = (
    types.ModuleType
    | type
    | types.MethodType
    | types.FunctionType
    | types.TracebackType
    | types.FrameType
    | types.CodeType
    | Callable[..., Any]
)

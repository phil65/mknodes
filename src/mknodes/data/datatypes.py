from __future__ import annotations

from collections.abc import Callable
import types
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Protocol, runtime_checkable


if TYPE_CHECKING:
    from dataclasses import Field


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

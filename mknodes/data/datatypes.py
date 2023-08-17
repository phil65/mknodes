from __future__ import annotations

from typing import Literal


AdmonitionTypeStr = Literal[
    "node",
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

PageStatusStr = Literal["new", "deprecated", "encrypted"]

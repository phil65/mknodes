"""Build output types."""

from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from mknodes.utils import resources as res


@dataclasses.dataclass
class BuildOutput:
    """Result of building a documentation tree."""

    files: dict[str, str | bytes] = dataclasses.field(default_factory=dict)
    """Mapping of file paths to markdown/content."""

    resources: res.Resources | None = None
    """Collected resources (JS, CSS, extensions)."""

    nav_structure: dict[str, Any] = dataclasses.field(default_factory=dict)
    """Navigation structure for downstream consumers."""

    page_count: int = 0
    """Number of pages built."""

    def __repr__(self) -> str:
        return f"{type(self).__name__}(files={len(self.files)}, pages={self.page_count})"

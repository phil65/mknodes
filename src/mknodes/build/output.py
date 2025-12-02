"""Build output types."""

from __future__ import annotations

import dataclasses
from typing import Any

from mknodes.utils import resources


@dataclasses.dataclass
class BuildOutput:
    """Result of building a documentation tree."""

    files: dict[str, str | bytes] = dataclasses.field(default_factory=dict)
    """Mapping of file paths to markdown/content."""

    file_resources: dict[str, resources.Resources] = dataclasses.field(default_factory=dict)
    """Mapping of file paths to their resources."""

    nav_structure: dict[str, Any] = dataclasses.field(default_factory=dict)
    """Navigation structure for downstream consumers."""

    page_count: int = 0
    """Number of pages built."""

    @property
    def merged_resources(self) -> resources.Resources:
        """Return all resources merged into one."""
        merged = resources.Resources()
        for res in self.file_resources.values():
            merged.merge(res)
        return merged

    def __repr__(self) -> str:
        return f"{type(self).__name__}(files={len(self.files)}, pages={self.page_count})"

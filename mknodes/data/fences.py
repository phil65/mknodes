from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from pymdownx import superfences


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclasses.dataclass(frozen=True)
class Fences:
    """Class describing a superfence.

    Arguments:
        name: name of the fence
        class_name: CSS class used by the fence
        format_fn: Callable for formatting
    """

    name: str
    class_name: str
    format_fn: str | Callable

    def as_dict(self):
        """Return fence data as a dictionary."""
        return {"name": self.name, "class": self.class_name, "format": self.format_fn}


mermaid_fence = Fences(
    name="mermaid",
    class_name="mermaid",
    format_fn=superfences.fence_code_format,
)

FENCES: dict[str, Fences] = {
    fence.name: fence
    for fence in [
        mermaid_fence,
    ]
}

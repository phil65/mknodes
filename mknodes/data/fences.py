from __future__ import annotations

from collections.abc import Callable
import dataclasses

from pymdownx import superfences


@dataclasses.dataclass(frozen=True)
class Fences:
    name: str
    class_name: str
    format_fn: str | Callable

    def as_dict(self):
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

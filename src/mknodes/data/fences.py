from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Any

from pymdownx import superfences  # type: ignore[import-untyped]

from mknodes.mdext.execute_ext import formatter as execute_formatter, validator as execute_validator


if TYPE_CHECKING:
    from collections.abc import Callable


@dataclasses.dataclass(frozen=True)
class Fences:
    """Class describing a superfence.

    Args:
        name: name of the fence
        class_name: CSS class used by the fence
        format_fn: Callable for formatting
        validator_fn: Optional callable for validation
    """

    name: str
    class_name: str
    format_fn: str | Callable[..., Any]
    validator_fn: Callable[..., bool] | None = None

    def as_dict(self) -> dict[str, Any]:
        """Return fence data as a dictionary."""
        result: dict[str, Any] = {
            "name": self.name,
            "class": self.class_name,
            "format": self.format_fn,
        }
        if self.validator_fn is not None:
            result["validator"] = self.validator_fn
        return result


mermaid_fence = Fences(
    name="mermaid",
    class_name="mermaid",
    format_fn=superfences.fence_code_format,  # pyright: ignore[reportUnknownMemberType, reportUnknownArgumentType]
)

python_exec_fence = Fences(
    name="python",
    class_name="python",
    format_fn=execute_formatter,
    validator_fn=execute_validator,
)

py_exec_fence = Fences(
    name="py",
    class_name="python",
    format_fn=execute_formatter,
    validator_fn=execute_validator,
)

FENCES: dict[str, Fences] = {
    fence.name: fence for fence in [mermaid_fence, python_exec_fence, py_exec_fence]
}

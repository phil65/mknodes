from __future__ import annotations

from typing import Any

from fieldz import fields

from mknodes.basenodes import mknode
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkDataClassInfo(mknode.MkNode):
    """Node for displaying dataclass-like object information."""

    ICON = "material/code-braces"

    def __init__(
        self,
        obj: Any,
        *,
        include_docstring: bool = True,
        skip_private: bool = True,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            obj: Dataclass-like object or class to display info for
            include_docstring: Whether to include docstring in output
            skip_private: Whether to skip fields starting with underscore
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.obj = obj
        self.include_docstring = include_docstring
        self.skip_private = skip_private

    @property
    def is_class(self) -> bool:
        """Return whether we're dealing with a class or an instance."""
        return isinstance(self.obj, type)

    async def to_md_unprocessed(self) -> str:
        """Convert the dataclass to markdown format."""
        try:
            obj_fields = fields(self.obj)
        except TypeError as e:
            msg = f"Unable to inspect fields of {type(self.obj)}"
            raise TypeError(msg) from e

        cls = self.obj if self.is_class else type(self.obj)
        lines = [f"### {cls.__name__}"]

        if self.include_docstring and cls.__doc__:
            lines.append(f"\n{cls.__doc__.strip()}\n")

        if self.is_class:
            lines.append("\n| Field | Description |")
            lines.append("|-------|-------------|")
        else:
            lines.append("\n| Field | Value | Description |")
            lines.append("|-------|--------|-------------|")

        for field in obj_fields:
            if self.skip_private and field.name.startswith("_"):
                continue

            type_str = f" *({field.type or 'any'})*" if field.type else ""
            name = f"`{field.name}`{type_str}"
            desc = field.description or ""

            if self.is_class:
                lines.append(f"| {name} | {desc} |")
            else:
                value = getattr(self.obj, field.name)
                lines.append(f"| {name} | `{value!r}` | {desc} |")

        return "\n".join(lines)


if __name__ == "__main__":
    from pydantic import BaseModel, ConfigDict

    # @dataclass
    class TestClass(BaseModel):
        """A test dataclass."""

        field_a: int
        """A description."""

        field_b: str = "default"
        model_config = ConfigDict(use_attribute_docstrings=True)

    test = TestClass(field_a=42)
    info = MkDataClassInfo(TestClass)
    print(info)

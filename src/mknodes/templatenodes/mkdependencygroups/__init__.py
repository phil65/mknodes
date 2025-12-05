from __future__ import annotations

from typing import Any, Literal

from mknodes.basenodes import mktable
from mknodes.info import parse_deps
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkDependencyGroups(mktable.MkTable):
    """Node to display optional dependencies or dependency groups as a table."""

    ICON = "material/package-variant"

    def __init__(self, source: Literal["extras", "groups"] = "extras", **kwargs: Any) -> None:
        """Constructor.

        Args:
            source: Where to read dependencies from:
                - "extras": `[project.optional-dependencies]`
                - "groups": `[dependency-groups]`
            kwargs: Keyword arguments passed to parent
        """
        self.source: Literal["extras", "groups"] = source
        super().__init__(**kwargs)

    def get_dependency_groups(self) -> list[parse_deps.DependencyGroup]:
        """Get dependency groups from pyproject.toml."""
        raw_text = self.ctx.metadata.pyproject_file.raw_text
        if not raw_text:
            return []
        return parse_deps.parse_dependencies(raw_text, source=self.source)

    @property
    def data(self) -> dict[str, list[Any]]:
        groups = self.get_dependency_groups()
        has_descriptions = any(g.description for g in groups)
        if has_descriptions:
            return {
                "Name": [g.name for g in groups],
                "Dependencies": [", ".join(g.dependencies) for g in groups],
                "Description": [g.description or "" for g in groups],
            }
        return {
            "Name": [g.name for g in groups],
            "Dependencies": [", ".join(g.dependencies) for g in groups],
        }

    @data.setter
    def data(self, value: dict[str, list[Any]]) -> None:
        # Required for MkTable compatibility but we compute data dynamically
        pass


if __name__ == "__main__":
    table = MkDependencyGroups.with_context()
    print(table)

from __future__ import annotations

import itertools
import textwrap

from typing import Any, Literal

from pymdownx import superfences

from mknodes.basenodes import mkcode
from mknodes.utils import helpers, resources


GraphTypeStr = Literal["flow", "sequence", "state"]

config = {
    "custom_fences": [
        {"name": "mermaid", "class": "mermaid", "format": superfences.fence_code_format},
    ],
}


class MkDiagram(mkcode.MkCode):
    """Class representing a mermaid diagram.

    MkDiagrams can show directed acyclic graphs and allows to manually
    create diagrams.
    """

    ICON = "material/graph-outline"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.superfences", **config)]

    TYPE_MAP = dict(
        flow="graph",
        sequence="sequenceDiagram",
        state="stateDiagram-v2",
    )

    def __init__(
        self,
        names: list[str] | None = None,
        connections: list[tuple] | None = None,
        *,
        graph_type: GraphTypeStr = "flow",
        direction: Literal["TD", "DT", "LR", "RL"] = "TD",
        attributes: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            names: names which should be part of the diagram
            connections: tuples indicating the connections of the names
            graph_type: Type of the graph
            direction: diagram direction
            attributes: Optional attributes for the names
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(language="mermaid", **kwargs)
        self._graph_type = graph_type
        self.direction = direction
        # Preserve order. Useful if only names are passed, order is important then.
        self.names = helpers.reduce_list(names or [])
        self.connections = set(connections or [])
        self.attributes = attributes or {}

    @property
    def graph_type(self) -> str:
        """The type of the graph (usually flow)."""
        return (
            self._graph_type
            if self._graph_type not in self.TYPE_MAP
            else self.TYPE_MAP[self._graph_type]
        )

    @property
    def text(self) -> str:
        """MkCode override."""
        return f"{self.graph_type} {self.direction}\n{self.mermaid_code}"

    @property
    def mermaid_code(self) -> str:
        """Return code block, excluding fences and (graph type direction) line.

        Can be overriden by subclasses.
        """
        lines = list(self.names)
        if not self.connections:
            lines = [f'{helpers.get_hash(i)}["{i}"]' for i in lines]
            for prev, nxt in itertools.pairwise(self.names):
                lines.append(f"{helpers.get_hash(prev)} --> {helpers.get_hash(nxt)}")
            return textwrap.indent("\n".join(lines), "  ")
        for connection in self.connections:
            if len(connection) == 2:  # noqa: PLR2004
                source, target = connection
                lines.append(f"{source} --> {target}")
            elif len(connection) == 3:  # noqa: PLR2004
                source, target, mark = connection
                lines.append(f"{source} --> |{mark}| {target}")
            else:
                msg = f"Tuple with wrong length: {connection}"
                raise TypeError(msg)
        return textwrap.indent("\n".join(lines), "  ")

    @property
    def fence_title(self) -> str:
        """MkCode override."""
        return "mermaid"

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += "MkDiagrams can be used to create Mermaid diagrams manually."
        diagram = MkDiagram(["1", "2", "3"], connections=[("1", "2"), ("2", "3")])
        page += mk.MkReprRawRendered(diagram, header="### Regular")
        diagram = MkDiagram(
            ["1", "2", "3"],
            connections=[("1", "2"), ("1", "3", "comment")],
            direction="LR",
        )
        page += mk.MkReprRawRendered(diagram, header="### Direction")


if __name__ == "__main__":
    diagram = MkDiagram(["a", "b", "c", "d"])
    print(diagram)

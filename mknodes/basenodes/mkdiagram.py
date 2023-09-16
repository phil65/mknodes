from __future__ import annotations

import textwrap

from typing import Any, Literal

from pymdownx import superfences

from mknodes.basenodes import mkcode
from mknodes.utils import reprhelpers


GraphTypeStr = Literal["flow", "sequence", "state"]

config = {
    "custom_fences": [
        {"name": "mermaid", "class": "mermaid", "format": superfences.fence_code_format},
    ],
}


class MkDiagram(mkcode.MkCode):
    """Class representing a mermaid diagram. Can show DAGs."""

    ICON = "material/graph-outline"
    REQUIRED_EXTENSIONS = {"pymdownx.superfences": config}

    TYPE_MAP = dict(
        flow="graph",
        sequence="sequenceDiagram",
        state="stateDiagram-v2",
    )
    ORIENTATION = dict(
        default="",
        left_right="LR",
        top_down="TD",
        right_left="RL",
        down_top="DT",
    )

    def __init__(
        self,
        graph_type: GraphTypeStr = "flow",
        *,
        items: list | None = None,
        connections: list[tuple] | None = None,
        direction: Literal["TD", "DT", "LR", "RL"] = "TD",
        attributes: dict[str, str] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            graph_type: Type of the graph
            items: items which should be part of the diagram
            connections: tuples indicating the connections of the items
            direction: diagram direction
            attributes: Optional attributes for the items
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(language="mermaid", **kwargs)
        self._graph_type = graph_type
        self._direction = direction
        self.names = set(items or [])
        self.connections = set(connections or [])
        self.attributes = attributes or {}

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            graph_type=self.graph_type,
            items=self.names,
            connections=self.connections,
            direction=self.direction,
        )

    @property
    def graph_type(self):
        return (
            self._graph_type
            if self._graph_type not in self.TYPE_MAP
            else self.TYPE_MAP[self._graph_type]
        )

    @property
    def direction(self):
        return (
            self._direction
            if self._direction not in self.ORIENTATION
            else self.ORIENTATION[self._direction]
        )

    @property
    def text(self):
        return f"{self.graph_type} {self.direction}\n{self.mermaid_code}"

    @property
    def mermaid_code(self):
        lines = list(self.names)
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
    def fence_title(self):
        return "mermaid"

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += "MkDiagrams can be used to create Mermaid diagrams manually."
        diagram = MkDiagram(items=["1", "2", "3"], connections=[("1", "2"), ("2", "3")])
        page += mknodes.MkReprRawRendered(diagram, header="### Regular")
        diagram = MkDiagram(
            items=["1", "2", "3"],
            connections=[("1", "2"), ("1", "3", "comment")],
            direction="LR",
        )
        page += mknodes.MkReprRawRendered(diagram, header="### Direction")


if __name__ == "__main__":
    diagram = MkDiagram(graph_type="flow")
    print(diagram)

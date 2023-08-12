from __future__ import annotations

import textwrap

from typing import Literal

from mknodes.basenodes import mkcode
from mknodes.utils import helpers


GraphTypeStr = Literal["flow", "sequence", "state"]


class MkDiagram(mkcode.MkCode):
    """Class representing a mermaid diagram. Can show DAGs."""

    ICON = "material/graph-outline"
    REQUIRED_EXTENSIONS = ["pymdownx.superfences"]

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
        header: str = "",
    ):
        """Constructor.

        Arguments:
            graph_type: Type of the graph
            items: items which should be part of the diagram
            connections: tuples indicating the connections of the items
            direction: diagram direction
            attributes: Optional attributes for the items
            header: Section header
        """
        super().__init__(language="mermaid", header=header)
        self.graph_type = (
            graph_type if graph_type not in self.TYPE_MAP else self.TYPE_MAP[graph_type]
        )
        self.direction = (
            direction
            if direction not in self.ORIENTATION
            else self.ORIENTATION[direction]
        )
        self.names = set(items or [])
        self.connections = set(connections or [])
        self.attributes = attributes or {}

    def __repr__(self):
        return helpers.get_repr(
            self,
            graph_type=self.graph_type,
            items=self.names,
            connections=self.connections,
            direction=self.direction,
        )

    @property
    def text(self):
        return f"{self.graph_type} {self.direction}\n{self.mermaid_code}"

    @property
    def mermaid_code(self):
        items = list(self.names) + [f"{a} --> {b}" for a, b in self.connections]
        return textwrap.indent("\n".join(items), "  ")

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
            connections=[("1", "2"), ("1", "3")],
            direction="LR",
        )
        page += mknodes.MkReprRawRendered(diagram, header="### Direction")


if __name__ == "__main__":
    diagram = MkDiagram(graph_type="flow")
    print(diagram)

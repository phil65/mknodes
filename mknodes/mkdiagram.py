from __future__ import annotations

import textwrap

from typing import Literal

from mknodes import mknode
from mknodes.utils import helpers


GraphTypeStr = Literal["flow", "sequence", "state"]


class MkDiagram(mknode.MkNode):
    """Class representing a mermaid diagram. Can show DAGs."""

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
        graph_type: GraphTypeStr,
        items=None,
        connections=None,
        orientation: Literal["TD", "DT", "LR", "RL"] = "TD",
        attributes: dict[str, str] | None = None,
        header: str = "",
    ):
        super().__init__(header=header)
        self.graph_type = (
            graph_type if graph_type not in self.TYPE_MAP else self.TYPE_MAP[graph_type]
        )
        self.orientation = (
            orientation
            if orientation not in self.ORIENTATION
            else self.ORIENTATION[orientation]
        )
        self.items = set(items or [])
        self.connections = set(connections or [])
        self.attributes = attributes or {}

    def __repr__(self):
        return helpers.get_repr(
            self,
            graph_type=self.graph_type,
            orientation=self.orientation,
        )

    def _to_markdown(self) -> str:
        items = list(self.items) + [f"{a} --> {b}" for a, b in self.connections]
        item_str = textwrap.indent("\n".join(items), "  ")
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"

    @staticmethod
    def examples():
        yield dict(
            graph_type="flow",
            items=["1", "2", "3"],
            connections=[("1", "2"), ("2", "3")],
        )


if __name__ == "__main__":
    diagram = MkDiagram(graph_type="flow")
    print(diagram)

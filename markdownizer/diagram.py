from __future__ import annotations

import itertools
import textwrap

from typing import Literal

from markdownizer import markdownnode, utils


GraphTypeStr = Literal["flow"]  # TODO


class Diagram(markdownnode.MarkdownNode):
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
        orientation: str = "TD",
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
        return utils.get_repr(
            self, graph_type=self.graph_type, orientation=self.orientation
        )

    def _to_markdown(self) -> str:
        items = list(self.items) + [f"{a} --> {b}" for a, b in self.connections]
        item_str = textwrap.indent("\n".join(items), "  ")
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


class ClassDiagram(Diagram):
    """Class diagram with several modes."""

    def __init__(
        self,
        klass: type,
        mode: Literal["parent_tree", "subclass_tree", "mro"] = "parent_tree",
        **kwargs,
    ):
        self.klass = klass
        self.mode = mode
        super().__init__(graph_type="flow", **kwargs)

    def __repr__(self):
        return utils.get_repr(
            self,
            klass=self.klass,
            mode=self.mode,
            orientation=self.orientation,
        )

    @staticmethod
    def examples():
        yield dict(klass=ClassDiagram)

    def _to_markdown(self) -> str:
        match self.mode:
            case "subclass_tree":
                items, connections = utils.get_connections(
                    [self.klass],
                    child_getter=lambda x: x.__subclasses__(),
                    id_getter=lambda x: x.__name__,
                )
            case "parent_tree":
                items, connections = utils.get_connections(
                    [self.klass],
                    child_getter=lambda x: x.__bases__,
                )
                items = [utils.label_for_class(i) for i in items]
                connections = [
                    (utils.label_for_class(i), utils.label_for_class(j))
                    for i, j in connections
                ]
            case "mro":
                items = [utils.label_for_class(i) for i in self.klass.mro()]
                connections = [
                    (utils.label_for_class(i), utils.label_for_class(j))
                    for i, j in itertools.pairwise(self.klass.mro())
                ]
            case _:
                raise ValueError(self.mode)
        items = list(items) + [f"{a} --> {b}" for a, b in connections]
        item_str = textwrap.indent("\n".join(items), "  ")
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


class MermaidMindMap(markdownnode.MarkdownNode):
    """Mermaid Mindmap to display trees."""

    def __init__(self, items: dict, header: str = ""):
        super().__init__(header=header)


if __name__ == "__main__":
    diagram = ClassDiagram(MermaidMindMap, mode="mro")
    print(diagram)

from __future__ import annotations

import textwrap

from typing import Literal

from markdownizer import markdownnode, utils


GraphTypeStr = Literal["flow"]  # TODO


def get_connections(objects, child_getter, id_getter=None):
    items = set()
    connections = []

    def add_connections(item):
        identifier = id_getter(item) if id_getter else item
        if identifier not in items:
            # if item.__module__.startswith(base_module):
            items.add(identifier)
            for base in child_getter(item):
                connections.append((id_getter(base) if id_getter else base, identifier))
                add_connections(base)

    for obj in objects:
        add_connections(obj)
    return items, connections


class MermaidDiagram(markdownnode.MarkdownNode):
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


class ClassDiagram(MermaidDiagram):
    """Class diagram with several modes."""

    def __init__(
        self,
        klass: type,
        mode: Literal["parent_tree", "subclass_tree"] = "parent_tree",
        *args,
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
        if self.mode == "subclass_tree":
            items, connections = get_connections(
                [self.klass],
                child_getter=lambda x: x.__subclasses__(),
                id_getter=lambda x: x.__name__,
            )
        else:
            items, connections = get_connections(
                [self.klass],
                child_getter=lambda x: x.__bases__,
            )
            items = [utils.label_for_class(i) for i in items]
            connections = [
                (utils.label_for_class(i), utils.label_for_class(j))
                for i, j in connections
            ]
        items = list(items) + [f"{a} --> {b}" for a, b in connections]
        item_str = textwrap.indent("\n".join(items), "  ")
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


class NodeDiagram(MermaidDiagram):
    """Can show the tree of a BaseNode."""

    def __init__(self, node: markdownnode.MarkdownNode, *args, **kwargs):
        self.node = node
        super().__init__(graph_type="flow", **kwargs)

    def __repr__(self):
        return utils.get_repr(self, node=self.node, orientation=self.orientation)

    def _to_markdown(self) -> str:
        items, connections = get_connections(
            [self.klass],
            child_getter=lambda x: x.children,
            id_getter=lambda x: repr(x),
        )
        items = list(items) + [f"{a} --> {b}" for a, b in connections]
        item_str = textwrap.indent("\n".join(items), "  ")
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


class MermaidMindMap(markdownnode.MarkdownNode):
    """Mermaid Mindmap to display trees."""

    def __init__(self, items: dict, header: str = ""):
        super().__init__(header=header)


if __name__ == "__main__":
    diagram = ClassDiagram(MermaidMindMap)
    print(diagram)

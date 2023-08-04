from __future__ import annotations

import itertools

from typing import Literal

from mknodes.basenodes import mkdiagram
from mknodes.utils import connector, helpers


DiagramModeStr = Literal["parent_tree", "subclass_tree", "mro"]


class BaseClassConnector(connector.Connector):
    def __init__(
        self,
        objects,
        *,
        title_style: Literal["package.classname", "qualname"] = "package.classname",
        max_depth: int | None = None,
    ):
        self.title_style = title_style
        # self.object = objects[0]
        super().__init__(objects, max_depth=max_depth)

    def get_id(self, item: type) -> int:
        return id(item)

    def get_title(self, item: type) -> str:
        return (
            helpers.label_for_class(item)
            if self.title_style == "package.classname"
            else item.__qualname__
        )
        # if item.__module__.split(".")[0] == self.object.__module__.split(".")[0]:
        #     return f"**{text}**"
        # else:
        #     return text

    def get_attributes(self, item) -> list[str]:
        return [i for i in dir(item) if not i.startswith("__")]


class SubclassConnector(BaseClassConnector):
    def _connect(self, objects):
        super()._connect(objects)
        self.connections = [(i[1], i[0]) for i in self.connections]

    def get_children(self, item: type) -> list[type]:
        return item.__subclasses__()


class ParentClassConnector(BaseClassConnector):
    def get_children(self, item: type) -> tuple[type, ...]:
        return item.__bases__


class MroConnector(BaseClassConnector):
    def _connect(self, objects):
        mro = list(objects[0].mro())[: self.max_depth]
        self.item_dict = {self.get_id(kls): self.get_title(kls) for kls in mro}
        self.connections = [
            (self.get_id(i), self.get_id(j)) for i, j in itertools.pairwise(mro)
        ]


class MkClassDiagram(mkdiagram.MkDiagram):
    """Class diagram with several modes."""

    def __init__(
        self,
        klass: type,
        mode: DiagramModeStr = "parent_tree",
        orientation: Literal["TD", "DT", "LR", "RL"] = "TD",
        max_depth: int | None = None,
        header: str = "",
    ):
        self.klass = klass
        self.mode = mode
        self._max_depth = max_depth
        super().__init__(
            graph_type="flow",
            orientation=orientation,
            header=header,
        )

    def __repr__(self):
        return helpers.get_repr(
            self,
            klass=self.klass,
            mode=self.mode,
            orientation=self.orientation,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        parent_diagram = MkClassDiagram(
            klass=MkClassDiagram,
            mode="parent_tree",
            header="Parent class hierarchy: MkClassDiagram",
        )
        sub_diagram = MkClassDiagram(
            klass=mknodes.MkContainer,
            mode="subclass_tree",
            header="Subclass hierarchy: MkContainer",
            orientation="LR",
        )
        mro_diagram = MkClassDiagram(
            klass=mknodes.MkTable,
            mode="mro",
            header="Method resolution order: MkTable",
        )
        page += mknodes.MkReprRawRendered(parent_diagram, indent=True)
        page += mknodes.MkReprRawRendered(sub_diagram, indent=True)
        page += mknodes.MkReprRawRendered(mro_diagram, indent=True)

    def _to_markdown(self) -> str:
        match self.mode:
            case "subclass_tree":
                builder = SubclassConnector(self.klass, max_depth=self._max_depth)
                item_str = builder.get_graph_connection_text()
            case "parent_tree":
                builder = ParentClassConnector(self.klass, max_depth=self._max_depth)
                item_str = builder.get_graph_connection_text()
            case "mro":
                builder = MroConnector(self.klass, max_depth=self._max_depth)
                item_str = builder.get_graph_connection_text()
            case _:
                raise ValueError(self.mode)
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


if __name__ == "__main__":
    from mknodes.basenodes import mknode

    diagram = MkClassDiagram(mknode.MkNode, mode="subclass_tree", max_depth=3)
    print(diagram)

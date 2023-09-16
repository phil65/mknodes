from __future__ import annotations

import itertools

from typing import Any, Literal

from mknodes.basenodes import mkdiagram
from mknodes.utils import classhelpers, connector, helpers, reprhelpers


DiagramModeStr = Literal["baseclasses", "subclasses", "mro"]


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
    """Node to display the class hierarchy of a class. Supports multiple modes."""

    def __init__(
        self,
        klass: type | str,
        mode: DiagramModeStr = "baseclasses",
        direction: Literal["TD", "DT", "LR", "RL"] = "TD",
        max_depth: int | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            klass: Klass to show a diagram for
            mode: What kind of diagram to display
            direction: diagram direction
            max_depth: Maxium depth to display
            kwargs: Keyword arguments passed to parent
        """
        self.klass = klass
        self.mode = mode
        self._max_depth = max_depth
        super().__init__(graph_type="flow", direction=direction, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            klass=self.klass,
            mode=self.mode,
            direction=self.direction,
        )

    @staticmethod
    def create_example_page(page):
        import mknodes

        parent_diagram = MkClassDiagram(klass=MkClassDiagram, mode="baseclasses")
        sub_diagram = MkClassDiagram(
            klass=mknodes.MkContainer,
            mode="subclasses",
            direction="LR",
        )
        mro_diagram = MkClassDiagram(klass=mknodes.MkTable, mode="mro")
        page += mknodes.MkReprRawRendered(
            parent_diagram,
            header="### Parent class hierarchy: MkClassDiagram",
        )
        page += mknodes.MkReprRawRendered(
            sub_diagram,
            header="### Subclass hierarchy: MkContainer",
        )
        page += mknodes.MkReprRawRendered(
            mro_diagram,
            header="### Method resolution order: MkTable",
        )

    @property
    def mermaid_code(self) -> str:
        klass = classhelpers.to_class(self.klass)
        match self.mode:
            case "subclasses":
                builder = SubclassConnector(klass, max_depth=self._max_depth)
                return builder.get_graph_connection_text()
            case "baseclasses":
                builder = ParentClassConnector(klass, max_depth=self._max_depth)
                return builder.get_graph_connection_text()
            case "mro":
                builder = MroConnector(klass, max_depth=self._max_depth)
                return builder.get_graph_connection_text()
            case _:
                raise ValueError(self.mode)


if __name__ == "__main__":
    from mknodes.basenodes import mknode

    diagram = MkClassDiagram(mknode.MkNode, mode="subclasses", max_depth=3)
    print(diagram)

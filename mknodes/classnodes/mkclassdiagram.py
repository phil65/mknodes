from __future__ import annotations

import itertools

from typing import Literal

from mknodes import mkdiagram
from mknodes.utils import connectionbuilder, helpers


DiagramModeStr = Literal["parent_tree", "subclass_tree", "mro"]


class BaseClassConnectionBuilder(connectionbuilder.ConnectionBuilder):
    def __init__(
        self,
        objects,
        *,
        title_style: Literal["package.classname", "qualname"] = "package.classname",
    ):
        self.title_style = title_style
        # self.object = objects[0]
        super().__init__(objects)

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


class SubclassConnectionBuilder(BaseClassConnectionBuilder):
    def _connect(self, objects):
        super()._connect(objects)
        self.connections = [(i[1], i[0]) for i in self.connections]

    def get_children(self, item: type) -> list[type]:
        return item.__subclasses__()


class ParentClassConnectionBuilder(BaseClassConnectionBuilder):
    def get_children(self, item: type) -> tuple[type, ...]:
        return item.__bases__


class MroConnectionBuilder(BaseClassConnectionBuilder):
    def _connect(self, objects):
        mro = list(objects[0].mro())
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
        header: str = "",
    ):
        self.klass = klass
        self.mode = mode
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
    def examples():
        yield dict(klass=MkClassDiagram)

    def _to_markdown(self) -> str:
        match self.mode:
            case "subclass_tree":
                builder = SubclassConnectionBuilder(self.klass)
                item_str = builder.get_graph_connection_text()
            case "parent_tree":
                builder = ParentClassConnectionBuilder(self.klass)
                item_str = builder.get_graph_connection_text()
            case "mro":
                builder = MroConnectionBuilder(self.klass)
                item_str = builder.get_graph_connection_text()
            case _:
                raise ValueError(self.mode)
        text = f"{self.graph_type} {self.orientation}\n{item_str}"
        return f"```mermaid\n{text}\n```"


if __name__ == "__main__":
    diagram = MkClassDiagram(MkClassDiagram, mode="mro")
    print(diagram)

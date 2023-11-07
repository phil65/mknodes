from __future__ import annotations as _annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, reprhelpers, resources


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


class MkAnnotation(mkcontainer.MkContainer):
    """Represents a single annotation. It gets managed by an MkAnnotations node."""

    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.superfences")]

    def __init__(
        self,
        num: int,
        content: str | mk.MkNode,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            num: Annotation index number
            content: Annotation content
            kwargs: Keyword arguments passed to parent
        """
        self.num = num
        super().__init__(content=content, **kwargs)

    def __repr__(self):
        return reprhelpers.get_repr(self, num=self.num, content=self.items)

    def _to_markdown(self) -> str:
        item_str = "\n\n".join(i.to_markdown() for i in self.items)
        lines = item_str.split("\n")
        space = (3 - len(str(self.num))) * " "
        result = [f"{self.num}.{space}{lines[0]}"]
        result.extend(f"    {i}" for i in lines[1:])
        return "\n".join(result) + "\n"


class MkAnnotations(mkcontainer.MkContainer):
    """Node containing a list of MkAnnotations."""

    items: list[MkAnnotation]
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.superfences")]
    ICON = "material/alert-box"

    def __init__(
        self,
        annotations: Mapping[int, str | mk.MkNode] | list[mk.MkNode | str] | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            annotations: Annotations data (Can be given in different shapes)
            kwargs: Keyword arguments passed to parent
        """
        match annotations:
            case None:
                items = []
            case list():
                items = [
                    (
                        ann if isinstance(ann, MkAnnotation) else MkAnnotation(i, ann)  # type: ignore
                    )
                    for i, ann in enumerate(annotations, start=1)
                ]
            case Mapping():
                items = [MkAnnotation(k, content=v) for k, v in annotations.items()]
            case _:
                raise TypeError(annotations)
        super().__init__(content=items, **kwargs)

    def __getitem__(self, item: int):
        for node in self.items:
            if node.num == item:
                return node
        raise IndexError(item)

    def __contains__(self, item: int | MkAnnotation) -> bool:
        match item:
            case MkAnnotation():
                return item in self.items
            case int():
                return any(i.num == item for i in self.items)
            case _:
                raise TypeError(item)

    def __repr__(self):
        notes = []
        for item in self.items:
            if len(item.items) == 1:
                item = reprhelpers.to_str_if_textnode(item.items[0])
            notes.append(item)
        return reprhelpers.get_repr(self, annotations=notes)

    def _get_item_pos(self, num: int) -> int:
        item = next(i for i in self.items if i.num == num)
        return self.items.index(item)

    def __setitem__(self, index: int, value: mk.MkNode | str):
        import mknodes as mk

        match value:
            case str():
                item = mk.MkText(value)
                node = MkAnnotation(index, content=item, parent=self)
            case MkAnnotation():
                node = value
            case mk.MkNode():
                node = MkAnnotation(index, content=value, parent=self)
        if index in self:
            pos = self._get_item_pos(index)
            self.items[pos] = node
        else:
            self.items.append(node)

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        page += mk.MkCode.for_object(
            MkAnnotations.create_example_page,
            extract_body=True,
        )
        node = MkAnnotations()
        page += node
        text = mk.MkText("The MkAnnotations node aggregates annotations(1).")
        page += text
        info = r"Annotations are numbered and can be set via \__setitem__."
        node[1] = info  # (1)
        admonition = mk.MkAdmonition("They can also contain other Markdown.")
        node[2] = admonition  # (2)
        text.annotations[1] = "Every MkNode can annotate via the 'annotations' attribute"
        page += mk.MkCode(str(node), language="markdown", header="Markdown")

    def _to_markdown(self) -> str:
        if not self.items:
            return ""
        items = sorted(self.items, key=lambda x: x.num)
        return "".join(i.to_markdown() for i in items)

    def annotate_text(self, markdown: str) -> str:
        if not self.items:
            return markdown
        return f'<div class="annotate" markdown>\n{markdown}\n</div>\n\n{self}'


if __name__ == "__main__":
    import mknodes as mk

    page = mk.MkPage()
    MkAnnotations.create_example_page(page)
    print(page)

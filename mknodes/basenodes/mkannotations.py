from __future__ import annotations

from collections.abc import Mapping
import logging

from typing import Any

from mknodes.basenodes import mkcontainer, mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkAnnotation(mkcontainer.MkContainer):
    """Represents a single annotation. It gets managed by an MkAnnotations node."""

    def __init__(
        self,
        num: int,
        content: str | mknode.MkNode,
        **kwargs,
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
        return helpers.get_repr(self, num=self.num, content=self.items)

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
    REQUIRED_EXTENSIONS = ["attr_list", "md_in_html", "pymdownx.superfences"]
    ICON = "material/alert-box"

    def __init__(
        self,
        annotations: Mapping[int, str | mknode.MkNode]
        | list[MkAnnotation]
        | list[str]
        | None = None,
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
                        ann
                        if isinstance(ann, MkAnnotation)
                        else MkAnnotation(i, ann)  # type: ignore
                    )
                    for i, ann in enumerate(annotations, start=1)
                ]
            case Mapping():
                items = [
                    MkAnnotation(
                        k,
                        content=mktext.MkText(v) if isinstance(v, str) else v,
                    )
                    for k, v in annotations.items()
                ]
        super().__init__(content=items, **kwargs)

    def __len__(self):
        return len(self.items)

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
            if len(item.items) == 1 and isinstance(item.items[0], mktext.MkText):
                notes.append(str(item.items[0]))
            elif len(item.items) == 1:
                notes.append(item.items[0])
            else:
                notes.append(item)
        return helpers.get_repr(self, annotations=notes)

    def _get_item_pos(self, num: int) -> int:
        item = next(i for i in self.items if i.num == num)
        return self.items.index(item)

    def __setitem__(self, index: int, value: mknode.MkNode | str):
        match value:
            case str():
                item = mktext.MkText(value)
                node = MkAnnotation(index, content=item)
            case MkAnnotation():
                node = value
            case mknode.MkNode():
                node = MkAnnotation(index, content=value)
        if index in self:
            pos = self._get_item_pos(index)
            self.items[pos] = node
        else:
            self.items.append(node)

    @staticmethod
    def create_example_page(page):
        import mknodes

        page += mknodes.MkCode.for_object(
            MkAnnotations.create_example_page,
            extract_body=True,
        )
        node = MkAnnotations()
        page += "The MkAnnotations node aggregates annotations."
        info = r"Annotations are numbered and can be set via \__setitem__."
        node[1] = info  # (1)
        admonition = mknodes.MkAdmonition("They can also contain other Markdown.")
        node[2] = admonition  # (2)
        page += node
        page += mknodes.MkCode(str(node), language="markdown", header="Markdown")

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
    import mknodes

    # ann = MkAnnotation(1, "test")
    # print(ann)
    page = mknodes.MkPage()
    MkAnnotations.create_example_page(page)
    print(page)

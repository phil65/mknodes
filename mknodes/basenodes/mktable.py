from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
import logging

from typing import Any

from mknodes.basenodes import mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkTable(mknode.MkNode):
    """Class representing a formatted table."""

    REQUIRED_EXTENSIONS = ["tables"]
    ICON = "octicons/table-24"

    def __init__(
        self,
        data: Sequence[Sequence[str]] | Sequence[dict] | dict[str, list] | None = None,
        columns: Sequence[str] | None = None,
        *,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            data: Data show for the table
            columns: Column headers if not provided by data.
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        match data:
            case () | None:
                self.data: dict[str, list[mknode.MkNode]] = {c: [] for c in columns or []}
            case Mapping():
                self.data = {
                    str(k): [self.to_item(i) for i in v] for k, v in data.items()
                }
            case ((str(), *_), *_):
                h = columns or [str(i) for i in range(len(data))]
                self.data = {}
                for i, col in enumerate(data):
                    self.data[h[i]] = [self.to_item(j) for j in col]
            case (dict(), *_):
                self.data = {
                    k: [self.to_item(dic[k]) for dic in data]  # type: ignore[index]
                    for k in data[0]
                }
            case _:
                raise TypeError(data)

    def __repr__(self):
        kwarg_data = {
            k: [str(i) if isinstance(i, mktext.MkText) else i for i in v]
            for k, v in self.data.items()
        }
        return helpers.get_repr(self, data=kwarg_data)

    @property
    def columns(self):
        return list(self.data.keys())

    @property
    def children(self):
        return [i for k in self.data for i in self.data[k]]

    @children.setter
    def children(self, data):
        match data:
            case Mapping():
                self.data = {
                    str(k): [self.to_item(i) for i in v] for k, v in data.items()
                }
            case (str(), *_):
                self.data = {"": [self.to_item(i) for i in data]}
            case (dict(), *_):
                self.data = {k: [self.to_item(dic[k]) for dic in data] for k in data[0]}
            case () | None:
                self.data = {}
            case _:
                raise TypeError(data)

    def to_item(self, i):
        item = mktext.MkText(i) if isinstance(i, str | None) else i
        item.parent_item = self
        return item

    def add_row(
        self,
        row: Sequence[str | None | mknode.MkNode] | dict[str, str | None],
    ):
        if len(row) != len(self.columns):
            msg = "Row to add doesnt have same length as header"
            raise ValueError(msg)
        match row:
            case dict():
                for k, v in row.items():
                    self.data[k].append(self.to_item(v))
            case _:
                for i, key in enumerate(self.data.keys()):
                    self.data[key].append(self.to_item(row[i]))

    def _to_markdown(self) -> str:
        if not any(self.data[k] for k in self.data):
            return ""
        formatters = [f"{{:<{self.width_for_column(c)}}}" for c in self.data]
        headers = [formatters[i].format(k) for i, k in enumerate(self.data.keys())]
        divider = [self.width_for_column(c) * "-" for c in self.data]
        data = [
            [
                formatters[i].format(str(k).replace("\n", "<br>"))
                for i, k in enumerate(row)
            ]
            for row in self._iter_rows()
        ]
        header_txt = "| " + " | ".join(headers) + " |"
        divider_text = "| " + " | ".join(divider) + " |"
        data_txt = ["| " + " | ".join(line) + " |" for line in data]
        return "\n".join([header_txt, divider_text, *data_txt]) + "\n"

    @staticmethod
    def create_example_page(page):
        import mknodes

        node_1 = MkTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
        # data can be given in different shapes.
        page += mknodes.MkNodeExample(node_1)
        dicts = [{"col 1": "abc", "col 2": "cde"}, {"col 1": "fgh", "col 2": "ijk"}]
        node_2 = MkTable(data=dicts)
        page += mknodes.MkNodeExample(node_2)

    def _iter_rows(self) -> Iterator[list[mknode.MkNode]]:
        length = min(len(i) for i in self.data.values())
        for j, _ in enumerate(range(length)):
            yield [self.data[k][j] for k in self.data]

    def width_for_column(self, column: str | int):
        """Returns the minimum width needed for given column.

        Arguments:
            column: Name or index of the column
        """
        if isinstance(column, int):
            column = list(self.data.keys())[column]
        max_len = max(
            (len(str(i).replace("\n", "<br>")) for i in self.data[column]),
            default=0,
        )
        return max(len(column), max_len)

    @classmethod
    def for_items(cls, items, columns: dict[str, Callable]):
        ls = [{k: v(item) for k, v in columns.items()} for item in items]
        return cls(ls)


if __name__ == "__main__":
    table = MkTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
    print(table)

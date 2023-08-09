from __future__ import annotations

from collections.abc import Callable, Iterator, Mapping, Sequence
import logging

from typing import Any

from mknodes.basenodes import mkcontainer, mknode, mktext
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkBaseTable(mkcontainer.MkContainer):
    """Base Class for MkTables. Only deals with managing the data.

    Subclasses can use other mechanisms for the rendering, like external libraries.
    """

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
            k: [helpers.to_str_if_textnode(i) for i in v] for k, v in self.data.items()
        }
        return helpers.get_repr(self, data=kwarg_data)

    @property
    def columns(self):
        return list(self.data.keys())

    @property
    def items(self):
        data = self.data  # property
        return [i for k in data for i in data[k]]

    @items.setter
    def items(self, data):
        match data:
            case Mapping():
                self.data = {
                    str(k): [self.to_item(i) for i in v] for k, v in data.items()
                }
            case (str(), *_):
                self.data = {"": [self.to_item(i) for i in data]}
            case (dict(), *_):
                self.data = {k: [self.to_item(dic[k]) for dic in data] for k in data[0]}
            case ():
                self.data = {"": [self.to_item(k) for k in data]}
            case None:
                self.data = {}
            case _:
                raise TypeError(data)

    def to_item(self, i):
        item = mktext.MkText(i) if isinstance(i, str | None) else i
        item.parent = self
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

    def iter_rows(self) -> Iterator[list[mknode.MkNode]]:
        data = self.data  # property
        length = min(len(i) for i in data.values())
        for j, _ in enumerate(range(length)):
            yield [data[k][j] for k in data]

    @classmethod
    def for_items(cls, items, columns: dict[str, Callable]):
        ls = [{k: v(item) for k, v in columns.items()} for item in items]
        return cls(ls)

    def width_for_column(self, column: str | int):
        """Returns the minimum width needed for given column.

        Arguments:
            column: Name or index of the column
        """
        data = self.data  # property
        if isinstance(column, int):
            column = list(data.keys())[column]
        max_len = max(
            (len(str(i).replace("\n", "<br>")) for i in data[column]),
            default=0,
        )
        return max(len(column), max_len)

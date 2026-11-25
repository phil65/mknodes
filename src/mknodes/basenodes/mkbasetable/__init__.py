from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING, Any, Self

from mknodes.basenodes import mkcontainer
from mknodes.utils import log, reprhelpers


if TYPE_CHECKING:
    from collections.abc import Callable, Iterator
    import mknodes as mk

logger = log.get_logger(__name__)


class MkBaseTable(mkcontainer.MkContainer):
    """Base Class for MkTables. Only deals with managing the data.

    Subclasses can use other mechanisms for the rendering, like external libraries.
    """

    ICON = "octicons/table-24"

    def __init__(
        self,
        data: Sequence[Sequence[str]]
        | Sequence[dict[str, mk.MkNode | str]]
        | Mapping[str, list[mk.MkNode | str]]
        | None = None,
        columns: Sequence[str] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Data can be given as:

        - a mapping column header -> cells (`{"Name": ["a", "b"], "Value": ["1", "2"]}`),
        - a list of rows (lists): `columns` are the headers, without `columns` the first
          row is the header (`[["Name", "Value"], ["a", "1"], ["b", "2"]]`),
        - a list of dicts (one per row, the keys of the first one are the headers).

        Args:
            data: Data show for the table
            columns: Column headers if not provided by data.
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        match data:
            case () | None:
                self._data: dict[str, list[mk.MkNode]] = {c: [] for c in columns or []}
            case Mapping():
                self._data = {str(k): [self.to_child_node(i) for i in v] for k, v in data.items()}
            case (first, *_) if _is_row(first):
                rows = [list(row) for row in data]  # type: ignore[arg-type]
                header = list(columns) if columns is not None else rows.pop(0)
                self._data = {str(h): [] for h in header}
                for row in rows:
                    self.add_row([row[i] if i < len(row) else "" for i in range(len(header))])
            case (dict(), *_):
                self._data = {k: [self.to_child_node(dic[k]) for dic in data] for k in data[0]}  # type: ignore[call-overload]
            case _:
                raise TypeError(data)

    def __repr__(self) -> str:
        kwarg_data = {
            k: [reprhelpers.to_str_if_textnode(i) for i in v] for k, v in self.data.items()
        }
        return reprhelpers.get_repr(self, data=kwarg_data)

    @property
    def data(self) -> dict[str, list[mk.MkNode]]:
        return self._data

    @data.setter
    def data(self, value: dict[str, list[mk.MkNode]]) -> None:
        self._data = value

    @property
    def columns(self):
        return list(self.data.keys())

    def get_items(self):
        return [i for k in self._data for i in self._data[k]]

    def set_items(self, data):  # pyright: ignore[reportIncompatibleMethodOverride]
        match data:
            case Mapping():
                self._data = {str(k): [self.to_child_node(i) for i in v] for k, v in data.items()}
            case (str(), *_):
                self._data = {"": [self.to_child_node(i) for i in data]}
            case (dict(), *_):
                self._data = {k: [self.to_child_node(dic[k]) for dic in data] for k in data[0]}
            case ():
                self._data = {"": [self.to_child_node(k) for k in data]}
            case None:
                self._data = {}
            case _:
                raise TypeError(data)

    def add_row(
        self,
        row: Sequence[str | mk.MkNode | None] | dict[str, str | None],
    ) -> None:
        if len(row) != len(self.columns):
            msg = "Row to add doesnt have same length as header"
            raise ValueError(msg)
        match row:
            case dict():
                for k, v in row.items():
                    self.data[k].append(self.to_child_node(_to_cell(v)))
            case _:
                for i, key in enumerate(self.data.keys()):
                    self.data[key].append(self.to_child_node(_to_cell(row[i])))

    def iter_rows(self) -> Iterator[list[mk.MkNode]]:
        data = self.data  # property
        length = min(len(i) for i in data.values())
        for j, _ in enumerate(range(length)):
            yield [data[k][j] for k in data]

    @classmethod
    def for_items(cls, items: list[dict[str, Any]], columns: dict[str, Callable[..., Any]]) -> Self:
        ls = [{k: v(item) for k, v in columns.items()} for item in items]
        return cls(ls)

    def width_for_column(self, column: str | int) -> int:
        """Returns the minimum width needed for given column.

        Args:
            column: Name or index of the column
        """
        data = self.data  # property
        col_name = list(data.keys())[column] if isinstance(column, int) else column
        col = data[col_name]
        max_len = max((len(str(i).replace("\n", "<br>")) for i in col), default=0)
        return max(len(col_name), max_len)


def _is_row(item: Any) -> bool:
    """Whether given item of the table data is a row (a list / tuple of cells)."""
    return isinstance(item, Sequence) and not isinstance(item, str | bytes)


def _to_cell(value: Any) -> Any:
    """Cells: nodes and strings stay, None becomes empty, other values text."""
    from mknodes.basenodes import mknode

    if value is None:
        return ""
    return value if isinstance(value, str | mknode.MkNode) else str(value)

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import logging

from mknodes import mknode


logger = logging.getLogger(__name__)


class MkTable(mknode.MkNode):
    """Class representing a formatted table."""

    REQUIRED_EXTENSIONS = "tables"

    def __init__(
        self,
        data: Sequence[Sequence[str]] | Sequence[dict] | dict[str, list] | None = None,
        columns: Sequence[str] | None = None,
        *,
        column_modifiers: dict[str, Callable[[str], str]] | None = None,
        header: str = "",
        **kwargs,
    ):
        super().__init__(header=header, **kwargs)
        column_modifiers = column_modifiers or {}
        match data:
            case None:
                self.data = {}
            case Mapping():
                self.data = {str(k): [str(i) for i in v] for k, v in data.items()}
            case ((str(), *_), *_):
                h = columns or [str(i) for i in range(len(data))]
                self.data = {}
                for i, col in enumerate(data):
                    self.data[h[i]] = [str(j) for j in col]
            case (dict(), *_):
                self.data = {k: [dic[k] for dic in data] for k in data[0]}  # type: ignore
            case ():
                self.data = {}
            case _:
                raise TypeError(data)
        for k, v in column_modifiers.items():
            self.data[k] = [v(i) for i in self.data[k]]

    def _to_markdown(self) -> str:
        if not any(self.data[k] for k in self.data):
            return ""
        formatters = [f"{{:<{self.width_for_column(c)}}}" for c in self.data]
        headers = [formatters[i].format(k) for i, k in enumerate(self.data.keys())]
        divider = [self.width_for_column(c) * "-" for c in self.data]
        data = [
            [formatters[i].format(k) for i, k in enumerate(row)]
            for row in self._iter_rows()
        ]
        header_txt = "| " + " | ".join(headers) + " |"
        divider_text = "| " + " | ".join(divider) + " |"
        data_txt = ["| " + " | ".join(line) + " |" for line in data]
        return "\n".join([header_txt, divider_text, *data_txt])

    @staticmethod
    def examples():
        yield dict(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
        dicts = [{"col 1": "abc", "col 2": "cde"}, {"col 1": "fgh", "col 2": "ijk"}]
        yield dict(data=dicts)

    def _iter_rows(self):
        length = min(len(i) for i in self.data.values())
        for j, _ in enumerate(range(length)):
            yield [self.data[k][j] or "" for k in self.data]

    def width_for_column(self, column: str | int):
        """Returns the minimum width needed for given column.

        Arguments:
            column: Name or index of the column
        """
        if isinstance(column, int):
            column = list(self.data.keys())[column]
        max_len = max((len(str(i)) for i in self.data[column]), default=0)
        return max(len(column), max_len)

    @classmethod
    def for_items(cls, items, columns: dict[str, Callable]):
        ls = [{k: v(item) for k, v in columns.items()} for item in items]
        return cls(ls)


if __name__ == "__main__":
    table = MkTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
    print(table)

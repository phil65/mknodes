from __future__ import annotations

from mknodes.basenodes import mkbasetable
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkTable(mkbasetable.MkBaseTable):
    """Class representing a formatted table."""

    REQUIRED_EXTENSIONS = ["tables"]

    def _to_markdown(self) -> str:
        table_data = self.data  # property
        if not any(table_data[k] for k in table_data):
            return ""
        widths = [self.width_for_column(c) for c in table_data]
        formatters = [f"{{:<{width}}}" for width in widths]
        headers = [formatters[i].format(k) for i, k in enumerate(table_data.keys())]
        divider = [width * "-" for width in widths]
        data = [
            [
                formatters[i].format(str(k).replace("\n", "<br>"))
                for i, k in enumerate(row)
            ]
            for row in self.iter_rows()
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
        page += mknodes.MkReprRawRendered(node_1, header="### From dict")
        dicts = [{"col 1": "abc", "col 2": "cde"}, {"col 1": "fgh", "col 2": "ijk"}]
        node_2 = MkTable(data=dicts)
        page += mknodes.MkReprRawRendered(node_2, header="### From list")


if __name__ == "__main__":
    table = MkTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
    print(table)

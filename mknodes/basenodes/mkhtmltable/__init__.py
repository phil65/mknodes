from __future__ import annotations

from mknodes.basenodes import mkbasetable
from mknodes.utils import log, xmlhelpers as xml


logger = log.get_logger(__name__)


class MkHtmlTable(mkbasetable.MkBaseTable):
    """Class representing a html table.

    Compared to MkTable, this will end up with a more verbose output,
    but it can contain more complex Markdown in cells.
    """

    STATUS = "new"

    def get_element(self) -> xml.Table | None:
        table_data = self.data  # property
        if not any(table_data[k] for k in table_data):
            return None
        root = xml.Table(markdown=True)
        data = [[str(k) for k in row] for row in self.iter_rows()]
        headers = list(table_data.keys())
        data.insert(0, headers)
        for items in data:
            tr = xml.Tr(parent=root)
            for item in items:
                td = xml.Td(parent=tr)
                td.text = "\n" + item + "\n"
        return root

    def _to_markdown(self) -> str:
        root = self.get_element()
        return root.to_string(space="") if root is not None else ""

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        code_col = [mk.MkCode("print('hello world')\nsys.exit()") for _ in range(3)]
        admonitions = [mk.MkAdmonition("Admonition inside cell") for _ in range(3)]
        tabs = [mk.MkTabbed(dict(A=["Tab a"], B=["Tab b"])) for _ in range(3)]
        data: dict[str, list] = dict(Code=code_col, Admonitions=admonitions, Tabs=tabs)
        page += mk.MkReprRawRendered(MkHtmlTable(data))


if __name__ == "__main__":
    table = MkHtmlTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
    print(table._to_markdown())

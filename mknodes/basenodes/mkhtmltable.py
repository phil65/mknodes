from __future__ import annotations

from mknodes.basenodes import mkbasetable
from mknodes.utils import log


logger = log.get_logger(__name__)


class MkHtmlTable(mkbasetable.MkBaseTable):
    """Class representing a html table.

    Compared to MkTable, this will end up with a more verbose output,
    but it can contain more complex Markdown in cells.
    """

    STATUS = "new"

    def _to_markdown(self) -> str:
        table_data = self.data  # property
        if not any(table_data[k] for k in table_data):
            return ""
        data = [[str(k) for k in row] for row in self.iter_rows()]
        headers = list(table_data.keys())
        data.insert(0, headers)
        text = '<table markdown="1">'
        for items in data:
            text += "\n\n<tr>"
            for item in items:
                text += "\n<td>\n"
                text += item
                text += "\n</td>"
            text += "\n</tr>"
        text += "\n</table>"
        return text

    @staticmethod
    def create_example_page(page):
        import mknodes

        code_col = [mknodes.MkCode("print('hello world')\nsys.exit()") for _ in range(3)]
        admonitions = [mknodes.MkAdmonition("Admonition inside cell") for _ in range(3)]
        tabs = [mknodes.MkTabbed(dict(A=["Tab a"], B=["Tab b"])) for _ in range(3)]
        data: dict[str, list] = dict(Code=code_col, Admonitions=admonitions, Tabs=tabs)
        page += mknodes.MkReprRawRendered(MkHtmlTable(data))


if __name__ == "__main__":
    table = MkHtmlTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
    print(table)

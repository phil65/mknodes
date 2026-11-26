import re

from mknodes import rendering
from mknodes.basenodes import mkbasetable
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


# A `|` not escaped yet / a code span (backticks, Python-Markdown keeps pipes in it).
PIPE_RE = re.compile(r"(?<!\\)\|")
CODE_SPAN_RE = re.compile(r"(`+)(?!`).+?(?<!`)\1(?!`)")


def escape_cell(text: str, *, in_code_spans: bool = True) -> str:
    """Make text usable as a Markdown table cell: escape `|`, newlines become `<br>`.

    Args:
        text: The cell text
        in_code_spans: Also escape pipes inside code spans (GFM needs that, Python-Markdown
                       shows the backslash there)
    """
    text = text.replace("\n", "<br>")
    if in_code_spans:
        return PIPE_RE.sub(r"\|", text)
    parts: list[str] = []
    pos = 0
    for match in CODE_SPAN_RE.finditer(text):
        parts.extend((PIPE_RE.sub(r"\|", text[pos : match.start()]), match.group()))
        pos = match.end()
    parts.append(PIPE_RE.sub(r"\|", text[pos:]))
    return "".join(parts)


class MkTable(mkbasetable.MkBaseTable):
    """Class representing a formatted table.

    Data: a mapping column -> cells, a list of rows (the first one is the header unless
    `columns` are given) or a list of dicts (see `MkBaseTable`). `|` in cells gets escaped.
    """

    REQUIRED_EXTENSIONS = [resources.Extension("tables")]

    async def to_md_unprocessed(self) -> str:
        table_data = self.data  # property
        if not any(table_data[k] for k in table_data):
            return ""
        in_code = rendering.current().name != "material"
        headers = [escape_cell(k, in_code_spans=in_code) for k in table_data]
        rows = [
            [escape_cell(str(cell), in_code_spans=in_code) for cell in row]
            for row in self.iter_rows()
        ]
        widths = [
            max(len(h), *(len(row[i]) for row in rows)) if rows else len(h)
            for i, h in enumerate(headers)
        ]
        formatters = [f"{{:<{width}}}" for width in widths]
        headers = [formatters[i].format(h) for i, h in enumerate(headers)]
        divider = [width * "-" for width in widths]
        data = [[formatters[i].format(c) for i, c in enumerate(row)] for row in rows]
        header_txt = "| " + " | ".join(headers) + " |"
        divider_text = "| " + " | ".join(divider) + " |"
        data_txt = ["| " + " | ".join(line) + " |" for line in data]
        return "\n".join([header_txt, divider_text, *data_txt]) + "\n"


if __name__ == "__main__":
    table = MkTable(data={"Column A": ["A", "B", "C"], "Column B": ["C", "D", "E"]})
    print(table)

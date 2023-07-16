from __future__ import annotations

import logging
import textwrap

from typing import Literal

from markdownizer import markdownnode


logger = logging.getLogger(__name__)

AdmonitionTypeStr = Literal[
    "node",
    "abstract",
    "info",
    "tip",
    "success",
    "question",
    "warning",
    "failure",
    "danger",
    "bug",
    "example",
    "quote",
]


class Admonition(markdownnode.Text):
    """[Admonition](https://squidfunk.github.io/mkdocs-material/reference/admonitions/) info box."""  # noqa: E501

    def __init__(
        self,
        typ: AdmonitionTypeStr,
        text: str,
        title: str | None = None,
        collapsible: bool = False,
        **kwargs,
    ):
        super().__init__(text=text, **kwargs)
        self.typ = typ
        self.title = title
        self.collapsible = collapsible

    def _to_markdown(self) -> str:
        block_start = "???" if self.collapsible else "!!!"
        title = f'"{self.title}"'
        text = textwrap.indent(str(self.text), "    ")
        return f"{block_start} {self.typ} {title}\n{text}\n\n"


# class TabWidget(Admonition):
#     def __init__(
#         self,
#         items=None,
#     ):
#         super().__init__(header=header)
#         self.items = items or []
#         self.title = title

#     def _to_markdown(self) -> str:
#         lines = [f'!!! Example "{self.title}"']

#         for item in self.items:
#             header = f"=== {header!r}"
#             text = textwrap.indent(item.to_markdown(), "        ")


if __name__ == "__main__":
    admonition = Admonition("info", "hello")
    print(admonition)

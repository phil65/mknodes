from __future__ import annotations

import logging
import textwrap

from typing import Literal

from mknodes import markdownnode


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
    """Admonition info box."""

    def __init__(
        self,
        text: str,
        typ: AdmonitionTypeStr = "info",
        *,
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
        title = f'"{self.title}"' if self.title else ""
        text = textwrap.indent(str(self.text), "    ")
        return f"{block_start} {self.typ} {title}\n{text}\n\n"

    @staticmethod
    def examples():
        for typ in [
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
        ]:
            yield dict(typ=typ, text=f"This is type {typ}", title=typ)
        yield dict(typ="info", text="This is a collapsible menu", collapsible=True)


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
    admonition = Admonition("hello")
    print(admonition)

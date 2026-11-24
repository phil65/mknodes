"""Convert Material for MkDocs block syntax in plain text to other output.

Nodes get rendered by renderer rules, but hand-written Markdown (texts, templates) may
contain Material syntax. This converts the common blocks:

- admonitions: `!!! note "Title"` / collapsible `??? note` / `???+ note`
- content tabs: `=== "Tab"`

Content of the blocks is indented by four spaces. Code fences are left untouched.
"""

from __future__ import annotations

import dataclasses
import re
import textwrap
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable


ADMONITION_RE = re.compile(
    r"^(?P<mark>!!!|\?\?\?\+?)\s+(?P<typ>[\w-]+)(?P<rest>[^\"]*?)"
    r"(?:\s*\"(?P<title>[^\"]*)\")?\s*$"
)
TAB_RE = re.compile(r"^===(?P<flag>[!+]?)\s+\"(?P<title>[^\"]*)\"\s*$")
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})")


@dataclasses.dataclass
class Admonition:
    typ: str
    title: str | None
    collapsible: bool
    expanded: bool
    text: str


@dataclasses.dataclass
class Tab:
    title: str
    selected: bool
    text: str


@dataclasses.dataclass
class Converters:
    """Output functions for the converted blocks."""

    admonition: Callable[[Admonition], str]
    tabs: Callable[[list[Tab]], str]


def convert(text: str, converters: Converters) -> str:
    """Convert Material blocks in given text (recursively, also inside blocks)."""
    lines = text.split("\n")
    out: list[str] = []
    i = 0
    fence: str | None = None
    while i < len(lines):
        line = lines[i]
        stripped = line.lstrip(" ")
        indent = line[: len(line) - len(stripped)]
        if fence:
            if stripped.startswith(fence) and not stripped[len(fence) :].strip():
                fence = None
            out.append(line)
            i += 1
            continue
        if m := FENCE_RE.match(stripped):
            fence = m["fence"]
            out.append(line)
            i += 1
            continue
        if m := ADMONITION_RE.match(stripped):
            body, i = _take_block(lines, i + 1, indent)
            mark = m["mark"]
            adm = Admonition(
                typ=m["typ"],
                title=m["title"],
                collapsible=mark.startswith("???"),
                expanded=mark == "???+",
                text=convert(body, converters),
            )
            out.extend(_indent(converters.admonition(adm), indent))
            continue
        if TAB_RE.match(stripped):
            tabs: list[Tab] = []
            while i < len(lines) and (m := TAB_RE.match(lines[i].removeprefix(indent))):
                body, i = _take_block(lines, i + 1, indent)
                selected = bool(m["flag"])
                tabs.append(Tab(m["title"], selected, convert(body, converters)))
                while i < len(lines) and not lines[i].strip():  # blanks between tabs
                    if i + 1 < len(lines) and TAB_RE.match(lines[i + 1].removeprefix(indent)):
                        i += 1
                    else:
                        break
            out.extend(_indent(converters.tabs(tabs), indent))
            continue
        out.append(line)
        i += 1
    return "\n".join(out)


def _take_block(lines: list[str], start: int, indent: str) -> tuple[str, int]:
    """Collect the lines indented below a block marker. Returns (dedented body, next index)."""
    inner = indent + "    "
    end = start
    last_content = start
    while end < len(lines):
        line = lines[end]
        if line.strip() and not line.startswith(inner):
            break
        if line.strip():
            last_content = end + 1
        end += 1
    body = "\n".join(lines[start:last_content])
    return textwrap.dedent(body), last_content


def _indent(text: str, indent: str) -> list[str]:
    return [f"{indent}{line}" if line else line for line in text.rstrip("\n").split("\n")]

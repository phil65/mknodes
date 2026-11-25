"""Convert Material for MkDocs block syntax in plain text to other output.

Nodes get rendered by renderer rules, but hand-written Markdown (texts, templates) may
contain Material syntax. This converts the common blocks:

- admonitions: `!!! note "Title"` / collapsible `??? note` / `???+ note`
- content tabs: `=== "Tab"`
- PyMdown blocks: `/// details | Title` ... `///` (optional converter)
- mkdocstrings directives: `::: dotted.path` + indented options (optional converter)
- optionally code fence options (`py title="x"`, `{.py title='x'}`), see `fence_info`

Content of the blocks is indented by four spaces. Code inside fences is left untouched.
"""

from __future__ import annotations

import dataclasses
import re
import textwrap
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from collections.abc import Callable


ADMONITION_RE = re.compile(
    r"^(?P<mark>!!!|\?\?\?\+?)\s+(?P<typ>[\w-]+)(?P<rest>[^\"]*?)"
    r"(?:\s*\"(?P<title>[^\"]*)\")?\s*$"
)
BLOCK_RE = re.compile(r"^(?P<slashes>/{3,})\s*(?P<name>[\w-]+)\s*(?:\|\s*(?P<arg>.*?))?\s*$")
AUTODOC_RE = re.compile(r"^:::\s+(?P<path>[\w.]+)\s*$")
TAB_RE = re.compile(r"^===(?P<flag>[!+]?)\s+\"(?P<title>[^\"]*)\"\s*$")
FENCE_RE = re.compile(r"^(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
ATTR_RE = re.compile(r"""(?P<key>[\w-]+)=(?P<quote>["']?)(?P<value>.*?)(?P=quote)(?:\s|$)""")


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
class Block:
    name: str
    """Block name (`details`, `note`, `html`, ...)."""
    argument: str | None
    """Text after the `|` (title), quotes removed."""
    text: str


@dataclasses.dataclass
class Converters:
    """Output functions for the converted blocks."""

    admonition: Callable[[Admonition], str]
    tabs: Callable[[list[Tab]], str]
    fence_info: Callable[[str, str], str] | None = None
    """Rewrite an opening code fence: `(fence, info string) -> line(s)` (None: keep)."""
    block: Callable[[Block], str] | None = None
    """Convert a PyMdown block (None: keep)."""
    autodoc: Callable[[str, dict[str, Any]], str] | None = None
    """Convert a `::: path` directive: `(path, options) -> Markdown` (None: keep)."""


def parse_fence_info(info: str) -> tuple[str, dict[str, str]]:
    """Split a Material code fence info string into language and options.

    Handles `py title="x" linenums="1"` and attribute lists (`{.py title='x'}`).
    """
    info = info.strip()
    if info.startswith("{") and info.endswith("}"):
        info = info[1:-1].strip()
    lang, _, rest = info.partition(" ")
    if "=" in lang:  # options only
        lang, rest = "", info
    lang = lang.removeprefix(".")
    options = {m["key"]: m["value"] for m in ATTR_RE.finditer(rest)}
    return lang, options


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
            if converters.fence_info and m["info"].strip():
                out.extend(_indent(converters.fence_info(fence, m["info"]), indent))
            else:
                out.append(line)
            i += 1
            continue
        if converters.block and (m := BLOCK_RE.match(stripped)):
            end = _find_block_end(lines, i + 1, indent + m["slashes"])
            if end is not None:
                body = "\n".join(line.removeprefix(indent) for line in lines[i + 1 : end])
                arg = (m["arg"] or "").strip().strip("\"'") or None
                block = Block(m["name"], arg, convert(_drop_options(body), converters))
                out.extend(_indent(converters.block(block), indent))
                i = end + 1
                continue
        if converters.autodoc and (m := AUTODOC_RE.match(stripped)):
            body, i = _take_block(lines, i + 1, indent)
            options = _parse_options(body)
            out.extend(_indent(converters.autodoc(m["path"], options), indent))
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


def _find_block_end(lines: list[str], start: int, closing: str) -> int | None:
    """Return the index of the closing `///` line of a block (None: unclosed)."""
    fence: str | None = None
    for i in range(start, len(lines)):
        stripped = lines[i].strip()
        if fence:
            if stripped.startswith(fence) and not stripped[len(fence) :].strip():
                fence = None
            continue
        if m := FENCE_RE.match(stripped):
            fence = m["fence"]
        elif lines[i].rstrip() == closing:
            return i
    return None


def _drop_options(body: str) -> str:
    """Drop the indented YAML options at the start of a PyMdown block."""
    lines = body.split("\n")
    i = 0
    while i < len(lines) and lines[i].startswith("    ") and ":" in lines[i]:
        i += 1
    return "\n".join(lines[i:]).strip("\n")


def _parse_options(body: str) -> dict[str, Any]:
    """Return the `options` of a `::: path` directive body (YAML)."""
    import yaml

    try:
        data = yaml.safe_load(body) if body.strip() else None
    except yaml.YAMLError:
        return {}
    options = data.get("options") if isinstance(data, dict) else None
    return options if isinstance(options, dict) else {}


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

"""Cheap sanity check for fenced code blocks of rendered pages.

A fence the Markdown engine doesn't recognise (e.g. an attribute list mangled from
`{.python title='x'}` to `<.python title='x'>`) shifts every following fence by one:
code gets shown as prose and prose as code until the end of the page.
"""

from __future__ import annotations

import re


FENCE_RE = re.compile(r"^(?P<indent>[ \t]*)(?P<fence>`{3,}|~{3,})(?P<info>.*)$")
# Info strings Python-Markdown / SuperFences / GitHub understand: nothing, a language
# (`python`, `.python`, `c++`, `objective-c`, `rust,ignore`, ...) optionally followed by
# options (`py title="x"`), an attribute list (`{.python title='x'}`) or a MyST
# directive (`{code-block} python`, `{toctree}`).
VALID_INFO_RE = re.compile(r"^(|\{[^{}]*\}|\{[\w-]+\}(\s+.*)?|[\w.+#-][^\s]*(\s+.*)?)$")


def check_fences(markdown: str) -> list[str]:
    """Return problems with the fenced code blocks of given Markdown.

    Reports opening fences with an info string no engine understands and fences
    left open at the end of the text.

    Args:
        markdown: The Markdown to check
    """
    problems: list[str] = []
    open_fence: tuple[str, int] | None = None  # (fence, line number)
    for lineno, line in enumerate(markdown.splitlines(), start=1):
        if not (match := FENCE_RE.match(line)):
            continue
        fence, info = match["fence"], match["info"].strip()
        if open_fence is not None:
            opener = open_fence[0]
            if not info and fence[0] == opener[0] and len(fence) >= len(opener):
                open_fence = None
            continue
        if fence[0] == "`" and "`" in info:  # inline code, not a fence
            continue
        if not VALID_INFO_RE.match(info):
            problems.append(f"line {lineno}: unrecognised code fence {line.strip()!r}")
        open_fence = (fence, lineno)
    if open_fence is not None:
        problems.append(f"line {open_fence[1]}: code fence {open_fence[0]!r} never closed")
    return problems

from __future__ import annotations

import re


CLASS_REGEX = re.compile(r"\b((mknodes\.Mk[A-Za-z\.\_]*).*)")


class AnnotationAppender:
    """Helper for auto-annotating code blocks.

    Example:
        test = "mknodes.MkAdmonition("test")"
        appender = AnnotationAppender()
        text = appender.append_markers(test)
        appender.append_annotations(node)

    """

    def __init__(self):
        self.count = 0
        self.matches = []

    def __call__(self, match) -> str:
        line = match.group()
        self.count += 1
        self.matches.append((self.count, match.group(2)))
        return f"{line} # ({self.count})"

    def append_markers(self, code: str) -> str:
        return re.sub(CLASS_REGEX, self, code) if "# (" not in code else code

    def append_annotations(self, node):
        import mknodes as mk

        for index, dotted_path in self.matches:
            node[index] = mk.MkDocStrings(dotted_path)

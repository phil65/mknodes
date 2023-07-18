from __future__ import annotations

from collections.abc import Callable
import logging

from markdownizer import code, markdownnode, utils


logger = logging.getLogger(__name__)


class SourceAndResult(markdownnode.MkNode):
    """Class to show the source of a Callable combined with its stringified result."""

    def __init__(self, fn: Callable, header: str = ""):
        super().__init__(header)
        self.fn = fn

    @staticmethod
    def examples():
        def test():
            return code.Code(language="py", code="a = 2 + 4")

        yield dict(fn=test)

    def __str__(self):
        return self.to_markdown()

    def __repr__(self):
        return utils.get_repr(self, fn=self.fn)

    def _to_markdown(self):
        code_block = code.Code.for_object(self.fn, extract_body=True)
        markdown = str(self.fn())
        return f"{code_block}\nresults in:\n\n{markdown}"


if __name__ == "__main__":
    test = code.Code(language="test")
    section = SourceAndResult(test.to_markdown, header="test")
    print(section.to_markdown())

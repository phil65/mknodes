from __future__ import annotations

from collections.abc import Callable
import logging

from mknodes import mkcode, mknode
from mknodes.utils import helpers


logger = logging.getLogger(__name__)


class MkSourceAndResult(mknode.MkNode):
    """Node for showing the source of a Callable combined with its stringified result."""

    def __init__(
        self,
        fn: Callable,
        header: str = "",
    ):
        super().__init__(header)
        self.fn = fn

    @staticmethod
    def examples():
        def test():
            return mkcode.MkCode(code="a = 2 + 4")

        yield dict(fn=test)

    def __str__(self):
        return self.to_markdown()

    def __repr__(self):
        return helpers.get_repr(self, fn=self.fn)

    def _to_markdown(self) -> str:
        code_block = mkcode.MkCode.for_object(self.fn, extract_body=True)
        markdown = str(self.fn())
        return f"{code_block}\nresults in:\n\n{markdown}"


if __name__ == "__main__":
    test = mkcode.MkCode(language="test")
    section = MkSourceAndResult(test.to_markdown, header="test")
    print(section.to_markdown())

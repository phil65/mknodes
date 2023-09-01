from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Any

from mknodes.basenodes import mknode
from mknodes.utils import reprhelpers


logger = logging.getLogger(__name__)


class MkCallable(mknode.MkNode):
    """Node carrying a callable. Can be either page, nav or node.

    The callable is called each time the virtual files are requested or when
    a Markdown conversion is requested.

    Experimental node. I do not really know yet what this should be good for. :)
    """

    ICON = "material/function"
    STATUS = "new"

    def __init__(
        self,
        fn: Callable[..., mknodes.MkNode],
        *,
        args: list | tuple | None = None,
        kw_args: dict | None = None,
        header: str = "",
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            fn: Callable (must return a MkNode).
            args: Arguments to use for callable
            kw_args: Keyword arguments to use for callable
            header: Section header
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(header=header, **kwargs)
        self.fn = fn
        self.args = args or []
        self.kw_args = kw_args or {}

    def __call__(self):
        node = self.fn(*self.args, **self.kw_args)
        node.parent = self.parent
        return node

    def __repr__(self):
        return reprhelpers.get_repr(
            self,
            fn=self.fn,
            args=self.args,
            kw_args=self.kw_args,
            _filter_empty=True,
        )

    def virtual_files(self):
        node = self.__call__()
        return node.virtual_files() | super().virtual_files()

    @staticmethod
    def create_example_page(page):
        import mknodes

        def make_page():
            page = mknodes.MkPage("MkCallable Page", virtual=True)
            page += "Content!"
            page += MkCallable(lambda: mknodes.MkAdmonition("Nested!"))
            return page

        node = MkCallable(fn=make_page)
        page += mknodes.MkReprRawRendered(node)

    def to_markdown(self) -> str:
        node = self.__call__()
        return node.to_markdown()


if __name__ == "__main__":
    import mknodes

    def make_page():
        page = mknodes.MkPage("test", hide_toc=True, virtual=True)
        page += "Some content"
        return page

    text = MkCallable(make_page, header="test")
    print(text.to_markdown())

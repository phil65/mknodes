from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mknode
from mknodes.utils import log, resources


if TYPE_CHECKING:
    import mknodes as mk


logger = log.get_logger(__name__)


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
        fn: Callable[..., mk.MkNode],
        *,
        args: list | tuple | None = None,
        kw_args: dict | None = None,
        **kwargs: Any,
    ):
        """Constructor.

        Arguments:
            fn: Callable (must return a MkNode).
            args: Arguments to use for callable
            kw_args: Keyword arguments to use for callable
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self.fn = fn
        self.args = args or []
        self.kw_args = kw_args or {}

    def __call__(self) -> mk.MkNode:
        node = self.fn(*self.args, **self.kw_args)
        node.parent = self.parent
        return node

    def children(self):
        node = self.__call__()
        return node.children

    def get_node_resources(self) -> resources.Resources:
        node = self.__call__()
        return node.get_node_resources()

    def to_markdown(self) -> str:
        node = self.__call__()
        return node.to_markdown()


if __name__ == "__main__":
    import mknodes as mk

    def make_page():
        page = mk.MkPage("test", hide="toc", inclusion_level=False)
        page += "Some content"
        return page

    text = MkCallable(make_page)
    print(text.to_markdown())

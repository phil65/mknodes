from __future__ import annotations

from collections.abc import Callable
import inspect
import logging
import types

from markdownizer import classhelpers, table, utils


logger = logging.getLogger(__name__)


class ModuleTable(table.Table):
    """Class representing a formatted table."""

    def __init__(
        self,
        module: types.ModuleType | str | tuple[str, ...],
        predicate: Callable | None = None,
        **kwargs,
    ):
        self.module = classhelpers.to_module(module, return_none=False)
        rows = [
            (
                submod_name,
                # utils.link_for_class(submod, size=4, bold=True),
                (
                    submod.__doc__.split("\n")[0]
                    if submod.__doc__
                    else "*No docstrings defined.*"
                ),
                (
                    utils.to_html_list(submod.__all__, make_link=True)
                    if hasattr(submod, "__all__")
                    else ""
                ),
            )
            for submod_name, submod in inspect.getmembers(self.module, inspect.ismodule)
            if (predicate is None or predicate(submod)) and "__" not in submod.__name__
        ]
        rows = list(zip(*rows))
        super().__init__(rows, columns=["Name", "Information", "Members"], **kwargs)

    # def __repr__(self):
    #     return utils.get_repr(self, module=self.module)

    @staticmethod
    def examples():
        import markdownizer

        yield dict(module=markdownizer)


if __name__ == "__main__":
    table = ModuleTable(module=utils)
    print(table)

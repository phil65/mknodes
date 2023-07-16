from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Literal

from markdownizer import table, utils


logger = logging.getLogger(__name__)


class BaseClassTable(table.Table):
    """Table showing info for a list of classes."""

    def __init__(
        self,
        klasses: list[type],
        layout: Literal["default", "extended"] = "default",
        filter_fn: Callable | None = None,
        *args,
        **kwargs,
    ):
        self.klasses = klasses
        if filter_fn is None:

            def always_true(_):
                return True

            self.filter_fn = always_true
        else:
            self.filter_fn = filter_fn
        # STRIP_CODE = r"```[^\S\r\n]*[a-z]*\n.*?\n```"
        # docs = [re.sub(STRIP_CODE, '', k.__module__, 0, re.DOTALL) for k in klasses]
        match layout:
            case "default":
                data = self.get_default_layout()
            case "extended":
                data = self.get_extended_layout()
            case _:
                raise ValueError(layout)

        super().__init__(data=data, **kwargs)

    def __repr__(self):
        return utils.get_repr(self, klasses=self.klasses)

    @staticmethod
    def examples():
        from markdownizer import nav, table

        yield dict(klasses=[table.Table, BaseClassTable, nav.Nav])
        yield dict(klasses=[table.Table, BaseClassTable, nav.Nav], layout="extended")

    def get_default_layout(self):
        desc = [
            kls.__doc__.split("\n")[0] if isinstance(kls.__doc__, str) else ""
            for kls in self.klasses
        ]
        return dict(
            Class=[utils.link_for_class(kls) for kls in self.klasses],
            Module=[kls.__module__ for kls in self.klasses],
            Description=desc,
        )

    def get_extended_layout(self, shorten_lists_after: int = 10):
        """Create a table containing information about a list of classes.

        Includes columns for child and parent classes including links.
        """
        ls = []
        for kls in self.klasses:
            subclasses = [
                subkls for subkls in kls.__subclasses__() if self.filter_fn(subkls)
            ]
            subclass_links = [utils.link_for_class(sub) for sub in subclasses]
            subclass_str = utils.to_html_list(
                subclass_links, shorten_after=shorten_lists_after
            )
            parents = kls.__bases__
            parent_links = [utils.link_for_class(parent) for parent in parents]
            parent_str = utils.to_html_list(
                parent_links, shorten_after=shorten_lists_after
            )
            desc = kls.__doc__.split("\n")[0] if isinstance(kls.__doc__, str) else ""
            desc = utils.escaped(desc)
            name = utils.link_for_class(kls, size=4, bold=True)
            module = utils.styled(kls.__module__, size=1, recursive=True)
            data = dict(
                Name=f"{name}<br>{module}<br>{desc}",
                # Module=kls.__module__,
                Children=subclass_str,
                Inherits=parent_str,
                # Description=desc,
            )
            ls.append(data)
        return ls


if __name__ == "__main__":
    table = BaseClassTable(klasses=[table.Table], layout="extended")
    print(table)

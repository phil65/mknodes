from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Literal

from mknodes.basenodes import mktable
from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class MkClassTable(mktable.MkTable):
    """Table showing info for a list of classes."""

    def __init__(
        self,
        klasses: list[type] | set[type],
        *,
        layout: Literal["compact", "extended"] = "extended",
        filter_fn: Callable | None = None,
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
            case "compact":
                data = [self.default_row_for_klass(kls) for kls in klasses]
            case "extended":
                data = [self.extended_row_for_klass(kls) for kls in klasses]
            case _:
                raise ValueError(layout)

        super().__init__(data=data, **kwargs)

    def __repr__(self):
        return helpers.get_repr(self, klasses=self.klasses)

    @staticmethod
    def create_example_page(page):
        import mknodes

        node_1 = MkClassTable(
            klasses=[mknodes.MkTable, MkClassTable, mknodes.MkNav],
            layout="compact",
            header="Compact layout",
        )
        node_2 = MkClassTable(
            klasses=[mknodes.MkTable, MkClassTable, mknodes.MkNav],
            layout="extended",
            header="Extended layout",
        )
        page += mknodes.MkReprRawRendered(node_1)
        page += mknodes.MkReprRawRendered(node_2)

    def default_row_for_klass(self, kls: type) -> dict[str, str]:
        return dict(
            Class=helpers.link_for_class(kls),
            Module=kls.__module__,
            Description=helpers.get_doc(kls, only_summary=True),
        )

    def extended_row_for_klass(
        self,
        kls: type,
        shorten_lists_after: int = 10,
    ) -> dict[str, str]:
        """Return a table row for given class.

        Includes columns for child and parent classes including links.
        """
        subclass_links = [
            helpers.link_for_class(sub)
            for sub in classhelpers.iter_subclasses(kls, recursive=False)
            if self.filter_fn(sub)
        ]
        subclass_str = helpers.to_html_list(
            subclass_links,
            shorten_after=shorten_lists_after,
        )
        parents = [
            base_kls
            for base_kls in kls.__bases__
            if "<locals>" not in base_kls.__qualname__  # filter locally defined
        ]
        parent_links = [helpers.link_for_class(parent) for parent in parents]
        parent_str = helpers.to_html_list(parent_links, shorten_after=shorten_lists_after)
        desc = helpers.get_doc(kls, escape=True, only_summary=True)
        name = helpers.link_for_class(kls, size=4, bold=True)
        module = helpers.styled(kls.__module__, size=1, recursive=True)
        return dict(
            Name=f"{name}<br>{module}<br>{desc}",
            # Module=kls.__module__,
            Children=subclass_str,
            Inherits=parent_str,
            # Description=desc,
        )


if __name__ == "__main__":
    table = MkClassTable(klasses=[mktable.MkTable], layout="extended")
    print(table)

from __future__ import annotations

import abc

from collections.abc import Callable
import logging
import types

from mknodes.utils import classhelpers, helpers


logger = logging.getLogger(__name__)


class Layout(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_row_for(self, obj):
        raise NotImplementedError


class CompactClassLayout(Layout):
    """Table showing info for a list of classes."""

    def __init__(self):
        super().__init__()

    def get_columns(self):
        return ["Class", "Module", "Description"]

    def get_row_for(self, kls: type) -> dict[str, str]:
        return dict(
            Class=helpers.link_for_class(kls),
            Module=kls.__module__,
            Description=helpers.get_doc(kls, only_summary=True),
        )


class ExtendedClassLayout(Layout):
    """Table showing info for a list of classes."""

    def __init__(self, subclass_predicate: Callable | None = None):
        if subclass_predicate is None:

            def always_true(_):
                return True

            self.subclass_predicate = always_true
        else:
            self.subclass_predicate = subclass_predicate
        super().__init__()

    def get_row_for(
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
            if self.subclass_predicate(sub)
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
        module = helpers.styled(kls.__module__, size=1, italic=True)
        return dict(
            Name=f"{name}<br>{module}<br>{desc}",
            # Module=kls.__module__,
            Children=subclass_str,
            Inherits=parent_str,
            # Description=desc,
        )

    def get_columns(self):
        return ["Name", "Children", "Inherits"]


class ModuleLayout(Layout):
    def get_row_for(self, module: types.ModuleType) -> dict[str, str]:
        fallback = "*No docstrings defined.*"
        return dict(
            Name=module.__name__,
            # helpers.link_for_class(submod, size=4, bold=True),
            DocStrings=helpers.get_doc(module, fallback=fallback, only_summary=True),
            Members=(
                helpers.to_html_list(module.__all__, make_link=True)
                if hasattr(module, "__all__")
                else ""
            ),
        )

    def get_columns(self):
        return ["Name", "DocStrings", "Members"]


if __name__ == "__main__":
    layout = ExtendedClassLayout()
    print(layout.get_row_for(ModuleLayout))

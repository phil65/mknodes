from __future__ import annotations

import abc

from collections.abc import Callable
import logging
import re
import types

from mknodes.basenodes import mkcontainer, mklink, mklist, mknode
from mknodes.info import packageinfo
from mknodes.templatenodes import mkmetadatabadges
from mknodes.utils import classhelpers, helpers, inspecthelpers, linkprovider


logger = logging.getLogger(__name__)

MARKER_RE = r'([A-Za-z_]* [>|=|<]* ".*?")'


class Layout(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_row_for(self, obj):
        raise NotImplementedError


class CompactClassLayout(Layout):
    """Table showing info for a list of classes."""

    def __init__(self, link_provider: linkprovider.LinkProvider | None = None):
        self.linkprovider = link_provider or linkprovider.LinkProvider()
        super().__init__()

    def get_columns(self):
        return ["Class", "Module", "Description"]

    def get_row_for(self, kls: type) -> dict[str, str]:
        return dict(
            Class=self.linkprovider.link_for_klass(kls),
            Module=kls.__module__,
            Description=inspecthelpers.get_doc(kls, only_summary=True),
        )


class ExtendedClassLayout(Layout):
    """Table showing info for a list of classes."""

    def __init__(
        self,
        link_provider: linkprovider.LinkProvider | None = None,
        subclass_predicate: Callable | None = None,
    ):
        self.linkprovider = link_provider or linkprovider.LinkProvider()
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
            self.linkprovider.link_for_klass(sub)
            for sub in classhelpers.iter_subclasses(kls, recursive=False)
            if self.subclass_predicate(sub)
        ]
        subclass_str = mklist.MkList(
            subclass_links,
            shorten_after=shorten_lists_after,
        )
        parents = [
            base_kls
            for base_kls in kls.__bases__
            if "<locals>" not in base_kls.__qualname__  # filter locally defined
        ]
        parent_links = [self.linkprovider.link_for_klass(parent) for parent in parents]
        parent_str = mklist.MkList(parent_links, shorten_after=shorten_lists_after)
        desc = inspecthelpers.get_doc(kls, escape=True, only_summary=True)
        link = self.linkprovider.link_for_klass(kls)
        name = helpers.styled(link, size=4, bold=True)
        module = helpers.styled(kls.__module__, size=1, italic=True)
        return dict(
            Name=f"{name}<br>{module}<br>{desc}",
            # Module=kls.__module__,
            Children=subclass_str.to_html(),
            Inherits=parent_str.to_html(),
            # Description=desc,
        )

    def get_columns(self):
        return ["Name", "Children", "Inherits"]


class ModuleLayout(Layout):
    def __init__(self, link_provider: linkprovider.LinkProvider | None = None):
        self.linkprovider = link_provider or linkprovider.LinkProvider()
        super().__init__()

    def get_row_for(self, module: types.ModuleType) -> dict[str, str]:
        fallback = "*No docstrings defined.*"
        doc = inspecthelpers.get_doc(module, fallback=fallback, only_summary=True)
        return dict(
            Name=self.linkprovider.link_for_module(module),
            DocStrings=doc,
            Members=(
                mklist.MkList(module.__all__, as_links=True, shorten_after=10).to_html()
                if hasattr(module, "__all__")
                else ""
            ),
        )

    def get_columns(self):
        return ["Name", "DocStrings", "Members"]


class BadgePackageLayout(Layout):
    def get_row_for(
        self,
        dependency: tuple[packageinfo.PackageInfo, packageinfo.Dependency],
    ) -> dict[str, str | mknode.MkNode]:
        package_info = dependency[0]
        dep_info = dependency[1]
        if url := package_info.homepage:
            node = mklink.MkLink(url, package_info.name)
        else:
            node = f"`{package_info.name}`"
        link = helpers.styled(str(node), size=3, bold=True)
        marker = str(dep_info.marker) if dep_info.marker else ""
        marker_str = re.sub(MARKER_RE, r"`\g<1>`", marker)
        summary = helpers.styled(package_info.metadata["Summary"], italic=True)
        info = mkmetadatabadges.MkMetadataBadges("websites", package=package_info.name)
        info.block_separator = "  "
        container_1 = mkcontainer.MkContainer([link, marker_str])
        container_1.block_separator = "\n"
        container_2 = mkcontainer.MkContainer([summary, info])
        return dict(Name=container_1, Summary=container_2)


class DefaultPackageLayout(Layout):
    def get_row_for(
        self,
        dependency: tuple[packageinfo.PackageInfo, packageinfo.Dependency],
    ) -> dict[str, str | mknode.MkNode]:
        package_info = dependency[0]
        dep_info = dependency[1]
        if url := package_info.homepage:
            node = mklink.MkLink(url, package_info.name)
        else:
            node = f"`{package_info.name}`"
        link = helpers.styled(str(node), size=3, bold=True)
        marker = str(dep_info.marker) if dep_info.marker else ""
        marker_str = re.sub(MARKER_RE, r"`\g<1>`", marker)
        summary = helpers.styled(package_info.metadata["Summary"], italic=True)
        return dict(Name=link, Summary=summary, Markers=marker_str)


if __name__ == "__main__":
    layout = ExtendedClassLayout()
    print(layout.get_row_for(ModuleLayout))

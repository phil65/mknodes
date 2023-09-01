from __future__ import annotations

from collections.abc import Callable
import logging

from typing import Any

from mkdocs import plugins

from mknodes.basenodes import (
    mkadmonition,
    mkcode,
    mkcontainer,
    mkheader,
    mklink,
    mknode,
    mkspeechbubble,
    mktext,
)
from mknodes.utils import inspecthelpers, reprhelpers


MKDOCS_LINK = "https://www.mkdocs.org/dev-guide/plugins/#{event}"

logger = logging.getLogger(__name__)


Flow = [
    "on_startup",
    "on_shutdown",
    "on_serve",
    "on_config",
    "on_pre_build",
    "on_files",
    "on_nav",
    "on_env",
    "on_post_build",
    "on_build_error",
    "on_pre_template",
    "on_template_context",
    "on_post_template",
    "on_pre_page",
    "on_page_read_source",
    "on_page_markdown",
    "on_page_content",
    "on_page_context",
    "on_post_page",
    "on_post_build",
    "on_serve",
    "on_shutdown",
]


def get_event_section(fn: Callable) -> list[mknode.MkNode]:
    code = mkcode.MkCode.for_object(fn)
    link = mklink.MkLink(MKDOCS_LINK.format(event=fn.__name__), fn.__name__)
    return [
        mkheader.MkHeader(link),
        mktext.MkText(inspecthelpers.get_doc(fn)),
        mkadmonition.MkAdmonition(code, collapsible=True, typ="quote", title="Source"),
    ]


class MkPluginFlow(mkcontainer.MkContainer):
    """Text node containing Instructions to set up a dev environment."""

    ICON = "material/dev-to"
    STATUS = "new"

    def __init__(self, plugin: type[plugins.BasePlugin] | None = None, **kwargs: Any):
        """Constructor.

        Arguments:
            plugin: MkDocs plugin
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(**kwargs)
        self._plugin = plugin
        self.block_separator = "\n"

    def __repr__(self):
        return reprhelpers.get_repr(self, plugin=self._plugin, _filter_empty=True)

    @property
    def plugin(self):
        match self._plugin:
            case None if self.associated_project:
                info = self.associated_project.info
                eps = info.get_entry_points("mkdocs.plugins")
                return next(iter(eps.values())) if eps else None
            case None:
                return None
            case _:
                return self._plugin

    @property
    def items(self):
        if not self.plugin:
            return []
        items = []
        for event in Flow:
            if not hasattr(self.plugin, event):
                continue
            fn = getattr(self.plugin, event)
            section = get_event_section(fn)
            bubble = mkspeechbubble.MkSpeechBubble(section, parent=self)
            items.append(bubble)
        if items:
            items[-1].arrow = None
        return items

    @items.setter
    def items(self, value):
        pass

    @staticmethod
    def create_example_page(page):
        from mkdocs.contrib import search

        import mknodes

        node = MkPluginFlow()
        page += mknodes.MkReprRawRendered(node, header="### From project")

        node = MkPluginFlow(plugin=search.SearchPlugin)
        page += mknodes.MkReprRawRendered(node, header="### Explicit")


if __name__ == "__main__":
    from mknodes import plugin

    setup_text = MkPluginFlow(plugin.MkNodesPlugin)

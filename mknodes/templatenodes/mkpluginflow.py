from __future__ import annotations

import logging

from typing import Any

from mkdocs import plugins

from mknodes.basenodes import (
    _mkdocstrings,
    mkadmonition,
    mkcode,
    mkcontainer,
    mkheader,
    mklink,
    mkspeechbubble,
    mktext,
)
from mknodes.data import eventplugins
from mknodes.utils import inspecthelpers, reprhelpers


logger = logging.getLogger(__name__)


class MkPluginFlow(mkcontainer.MkContainer):
    """Text node containing Instructions to set up a dev environment."""

    ICON = "material/dev-to"
    STATUS = "new"
    REQUIRED_EXTENSIONS = ["md_in_html"]

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
                return next(iter(eps.values())).obj if eps else None
            case None:
                return None
            case _:
                return self._plugin

    @property
    def event_plugin(self):
        return eventplugins.mkdocs_plugin

    @property
    def items(self):
        if not self.plugin:
            return []
        items = [mkheader.MkHeader(self.plugin.__name__, parent=self)]
        for event in self.event_plugin.flow:
            if not hasattr(self.plugin, event):
                continue
            fn = getattr(self.plugin, event)
            code = mkcode.MkCode.for_object(fn)
            fn_name = fn.__name__
            link = self.event_plugin.help_link.format(event=fn_name)
            link = mklink.MkLink(link, fn_name)
            hook_path = self.event_plugin.hook_fn_path.format(event=fn_name)
            info = _mkdocstrings.MkDocStrings(hook_path, show_source=False)
            section = [
                mkheader.MkHeader(link),
                mktext.MkText(inspecthelpers.get_doc(fn)),
                mkadmonition.MkAdmonition(
                    code,
                    collapsible=True,
                    typ="quote",
                    title="Source",
                ),
                mkadmonition.MkAdmonition(info, collapsible=True, title="Hook info"),
            ]
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

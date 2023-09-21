from __future__ import annotations

from typing import Any

from mkdocs import plugins

from mknodes.basenodes import mkcontainer
from mknodes.data import eventplugins
from mknodes.utils import inspecthelpers, log, reprhelpers, requirements


logger = log.get_logger(__name__)


class MkPluginFlow(mkcontainer.MkContainer):
    """Node showing info about the different stages of an MkDocs plugin."""

    ICON = "material/dev-to"
    STATUS = "new"
    REQUIRED_EXTENSIONS = [requirements.Extension("md_in_html")]

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
    def plugins(self):
        match self._plugin:
            case None:
                eps = self.ctx.metadata.entry_points
                return [i.obj for i in eps.values() if i.group == "mkdocs.plugins"]
            case _:
                return [self._plugin]

    @property
    def event_plugin(self):
        return eventplugins.mkdocs_plugin

    @property
    def items(self):
        import mknodes as mk

        if not self.plugins:
            return []
        items = []
        for plg in self.plugins:
            section = [
                mk.MkHeader(plg.__name__, parent=self),
                mk.MkHeader("Config", parent=self, level=3),
                mk.MkDocStrings(
                    plg.config_class,
                    parent=self,
                    show_root_toc_entry=False,
                    show_if_no_docstring=True,
                    heading_level=4,
                    show_bases=False,
                    show_source=False,
                ),
            ]
            for event in self.event_plugin.flow:
                if not hasattr(plg, event):
                    continue
                fn = getattr(plg, event)
                code = mk.MkCode.for_object(fn)
                fn_name = fn.__name__
                link = self.event_plugin.help_link.format(event=fn_name)
                link = mk.MkLink(link, fn_name)
                path = self.event_plugin.hook_fn_path.format(event=fn_name)
                info = mk.MkDocStrings(path, show_source=False, show_root_toc_entry=False)
                bubble_content = [
                    mk.MkHeader(link, level=3),
                    mk.MkText(inspecthelpers.get_doc(fn)),
                    mk.MkAdmonition(code, collapsible=True, typ="quote", title="Source"),
                    mk.MkAdmonition(info, collapsible=True, title="Hook info"),
                ]
                bubble = mk.MkSpeechBubble(bubble_content, parent=self)
                section.append(bubble)
            if section:
                section[-1].arrow = None
            items.extend(section)
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
    node = MkPluginFlow.with_default_context()
    print(node)

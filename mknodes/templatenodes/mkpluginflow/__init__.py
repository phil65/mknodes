from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.basenodes import mkcontainer
from mknodes.data import eventplugins
from mknodes.utils import classhelpers, inspecthelpers, log, reprhelpers


if TYPE_CHECKING:
    from mkdocs import plugins


logger = log.get_logger(__name__)


class MkPluginFlow(mkcontainer.MkContainer):
    """Node showing info about the different stages of an MkDocs plugin."""

    ICON = "material/dev-to"
    STATUS = "new"
    VIRTUAL_CHILDREN = True

    def __init__(
        self,
        plugin: type[plugins.BasePlugin] | str | None = None,
        **kwargs: Any,
    ):
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
                ep_group = self.event_plugin.entry_point_group
                eps = self.ctx.metadata.entry_points.get(ep_group, [])
                return [i.load() for i in eps]
            case type():
                return [self._plugin]
            case str():
                return [classhelpers.to_class(self._plugin)]
            case _:
                raise TypeError(self._plugin)

    @property
    def event_plugin(self):
        return eventplugins.mkdocs_plugin

    def hooks_for_plugin(self, plugin):
        return [e for e in self.event_plugin.flow if hasattr(plugin, e)]

    @property
    def items(self):
        import mknodes as mk

        if not self.plugins:
            return []
        items = []
        for plg in self.plugins:
            section = [mk.MkHeader(plg.__name__, parent=self)]
            for event in self.hooks_for_plugin(plg):
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
            if section and isinstance(section[-1], mk.MkSpeechBubble):
                section[-1].arrow = None
            items.extend(section)
        return items

    @items.setter
    def items(self, value):
        pass

    @classmethod
    def create_example_page(cls, page):
        from mkdocs.contrib import search

        import mknodes as mk

        node = MkPluginFlow(plugin=search.SearchPlugin)
        page += mk.MkReprRawRendered(node)


if __name__ == "__main__":
    node = MkPluginFlow.with_context()
    print(node)

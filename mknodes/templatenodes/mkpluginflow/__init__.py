from __future__ import annotations

from typing import TYPE_CHECKING, Any

from mknodes.templatenodes import mktemplate
from mknodes.data import eventplugins
from mknodes.utils import classhelpers, log


if TYPE_CHECKING:
    from mkdocs import plugins


logger = log.get_logger(__name__)


class MkPluginFlow(mktemplate.MkTemplate):
    """Node showing info about the different stages of an MkDocs plugin."""

    ICON = "material/dev-to"
    STATUS = "new"

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
        super().__init__("output/markdown/template", **kwargs)
        self._plugin = plugin

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


if __name__ == "__main__":
    from mkdocs.contrib import search

    node = MkPluginFlow(plugin=search.SearchPlugin)
    print(node)

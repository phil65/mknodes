from __future__ import annotations

from mknodes.basenodes import mktabcontainer, mktabs
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTabbed(mktabcontainer.MkTabContainer):
    """PyMdown-based Tab container."""

    items: list[mktabs.MkTab]
    REQUIRED_EXTENSIONS = [
        resources.Extension("pymdownx.tabbed"),
        resources.Extension("pymdownx.superfences"),
    ]
    Tab = mktabs.MkTab

    @classmethod
    def create_example_page(cls, page):
        import mknodes as mk

        # this node is basically a container and manager for MkTabs nodes.
        node = MkTabbed(tabs={"Tab 1": "Some markdown", "Tab 2": "Other Markdown"})
        page += mk.MkReprRawRendered(node, header="### Regular")
        admonition = mk.MkAdmonition("Nested admonition")
        nested_node = MkTabbed(tabs={"Tabs": node, "Admonition": admonition})
        page += mk.MkReprRawRendered(nested_node, header="### Nested")


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabbed = MkTabbed(tabs)
    print(tabbed)

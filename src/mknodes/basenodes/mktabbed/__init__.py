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


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabbed = MkTabbed(tabs)
    print(tabbed)

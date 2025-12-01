from __future__ import annotations

from mknodes.basenodes import mktabs, mktabcontainer
from mknodes.utils import log, resources


logger = log.get_logger(__name__)


class MkTabbedBlocks(mktabcontainer.MkTabContainer):
    """PyMdown Block Extension Tab."""

    items: list[mktabs.MkTabBlock]
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.blocks.tab")]
    Tab = mktabs.MkTabBlock


if __name__ == "__main__":
    tabs = dict(Tab1="Some text", Tab2="Another text")
    tabblock = MkTabbedBlocks(tabs)
    print(tabblock)

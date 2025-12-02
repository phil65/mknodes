"""Simple standalone build script for testing the mknodes CLI.

Usage:
    mknodes -s mknodes.manual.standalone:build -o ./docs
"""

from __future__ import annotations

import mknodes as mk
from mknodes.manual import (
    dev_section,
    get_started_section,
    navs_section,
    nodes_section,
    page_section,
    templating_section,
)


def build(root: mk.MkNav) -> mk.MkNav:
    """Build a simple documentation structure.

    Args:
        root: Root navigation node to populate.

    Returns:
        The populated navigation node.
    """
    # Create index page
    index = root.add_page("Welcome", is_index=True)
    index += mk.MkHeader("Welcome to MkNodes")
    index += mk.MkText("This is a simple example of standalone mknodes documentation.")
    index += mk.MkAdmonition(
        "MkNodes lets you build documentation programmatically!",
        typ="info",
        title="About MkNodes",
    )
    root.page_template.announcement_bar = mk.MkMetadataBadges("websites")
    root += get_started_section.nav
    root += navs_section.nav
    root += page_section.nav
    root += nodes_section.nav
    root += templating_section.nav
    root += dev_section.nav
    return root


if __name__ == "__main__":
    # Quick test: build and print structure
    nav = mk.MkNav()
    build(nav)
    for level, node in nav.iter_nodes():
        indent = "  " * level
        print(f"{indent}{type(node).__name__}: {getattr(node, 'title', '')}")

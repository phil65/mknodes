"""Simple standalone build script for testing the mknodes CLI.

Usage:
    mknodes -s mknodes.manual.standalone:build -o ./docs
"""

from __future__ import annotations

import mknodes as mk


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

    # Create a getting started section
    getting_started = root.add_nav("Getting Started")

    install_page = getting_started.add_page("Installation")
    install_page += mk.MkHeader("Installation")
    install_page += mk.MkCode("pip install mknodes", language="bash")

    usage_page = getting_started.add_page("Basic Usage")
    usage_page += mk.MkHeader("Basic Usage")
    usage_page += mk.MkText("Create a build script and run the CLI:")
    usage_page += mk.MkCode(
        """
import mknodes as mk

def build(root: mk.MkNav) -> mk.MkNav:
    page = root.add_page("Hello", is_index=True)
    page += mk.MkText("Hello, World!")
    return root
""".strip(),
        language="python",
    )

    # Create an examples section
    examples = root.add_nav("Examples")

    nodes_page = examples.add_page("Node Examples")
    nodes_page += mk.MkHeader("Available Nodes")
    nodes_page += mk.MkText("MkNodes provides many node types:")

    nodes_page += mk.MkHeader("Admonitions", level=2)
    nodes_page += mk.MkAdmonition("This is a note", typ="note", title="Note")
    nodes_page += mk.MkAdmonition("This is a warning", typ="warning", title="Warning")
    nodes_page += mk.MkAdmonition("This is a tip", typ="tip", title="Tip")

    nodes_page += mk.MkHeader("Code Blocks", level=2)
    nodes_page += mk.MkCode("print('Hello, World!')", language="python")

    nodes_page += mk.MkHeader("Lists", level=2)
    nodes_page += mk.MkList(["Item 1", "Item 2", "Item 3"])

    return root


if __name__ == "__main__":
    # Quick test: build and print structure
    nav = mk.MkNav()
    build(nav)
    for level, node in nav.iter_nodes():
        indent = "  " * level
        print(f"{indent}{type(node).__name__}: {getattr(node, 'title', '')}")

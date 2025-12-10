"""MkNodes Markdown Extension.

A pymdownx-based block extension that allows rendering Jinja templates
using the MkNodes NodeEnvironment within markdown documents.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any
import xml.etree.ElementTree as ET

from pymdownx.blocks import BlocksExtension  # type: ignore[import-untyped]
from pymdownx.blocks.block import Block  # type: ignore[import-untyped]


if TYPE_CHECKING:
    from mknodes.jinja.nodeenvironment import NodeEnvironment


class MkNodesBlock(Block):
    """A block for rendering Jinja templates using MkNodes."""

    NAME = "mknodes"
    ARGUMENT = None  # Optional argument for per-block context mode

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the MkNodes block processor."""
        super().__init__(*args, **kwargs)
        self._node_env: NodeEnvironment | None = None

    def _get_node_environment(self):
        """Get or create a NodeEnvironment for rendering."""
        if self._node_env is None:
            # Import here to avoid circular imports
            import mknodes as mk

            # Check context: per-block argument takes precedence over global config
            use_context = False  # default: no context (fast)

            # Check for per-block argument first (e.g., /// mknodes | context)
            if hasattr(self, "argument") and self.argument:
                arg = self.argument.strip().lower()
                use_context = arg in ("context", "true", "1", "yes")

            # Fall back to global config if no block argument specified
            elif hasattr(self, "config"):
                use_context = self.config.get("context", False)

            node = mk.MkText.with_context() if use_context else mk.MkText()

            from mknodes.jinja.nodeenvironment import NodeEnvironment

            self._node_env = NodeEnvironment(node)
        return self._node_env

    def on_create(self, parent: ET.Element) -> ET.Element:
        """Create the container element for the rendered content."""
        # Create a div container that will hold the rendered markdown
        return ET.SubElement(parent, "div", {"class": "mknodes-block"})

    def on_end(self, block: ET.Element) -> None:
        """Process the block content and render using NodeEnvironment."""
        # Extract text content from child elements since the content
        # has already been processed into HTML elements
        jinja_content = ""

        for child in block:
            if child.text:
                jinja_content += child.text
            if child.tail:
                jinja_content += child.tail

        jinja_content = jinja_content.strip()

        if not jinja_content:
            return

        try:
            # Get the NodeEnvironment and render the Jinja content
            env = self._get_node_environment()
            rendered_markdown = env.render_string(jinja_content)

            # Clear the block and set it to handle markdown content
            block.clear()

            # The rendered content is markdown, so we need to parse it
            if rendered_markdown.strip():
                # Import markdown to parse the rendered content
                import markdown

                # Create a markdown instance with extensions that MkNodes uses
                md = markdown.Markdown(
                    extensions=[
                        "admonition",
                        "pymdownx.superfences",
                        "pymdownx.highlight",
                        "pymdownx.progressbar",
                        "tables",
                        "fenced_code",
                    ]
                )
                rendered_html = md.convert(rendered_markdown)

                # Create a div to hold the HTML content
                content_div = ET.SubElement(block, "div")
                content_div.set("class", "mknodes-rendered")

                # Parse the HTML and add it to our div
                try:
                    # Parse the HTML string into elements
                    html_fragment = f"<div>{rendered_html}</div>"
                    parsed = ET.fromstring(html_fragment)

                    # Move all children from parsed div to our content div
                    for child in parsed:
                        content_div.append(child)

                    # Also set the text content if there is any
                    if parsed.text:
                        content_div.text = parsed.text

                except ET.ParseError:
                    # If parsing fails, just set as text
                    content_div.text = rendered_html

        except Exception as e:  # noqa: BLE001
            # On error, show the error message
            block.clear()
            error_elem = ET.SubElement(block, "div")
            error_elem.set("class", "mknodes-error")
            error_elem.set("style", "color: red; border: 1px solid red; padding: 0.5rem;")
            error_elem.text = f"MkNodes rendering error: {e}"


class MkNodesExtension(BlocksExtension):
    """Extension for MkNodes blocks."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the extension."""
        self.config = {
            "context": [
                False,
                "Whether to create full project context (expensive). Default: False",
            ]
        }
        super().__init__(*args, **kwargs)

    def extendMarkdownBlocks(self, md, block_mgr):  # noqa: N802
        """Register the MkNodes block with the block manager."""
        block_mgr.register(MkNodesBlock, self.getConfigs())


def makeExtension(**kwargs: Any):  # noqa: D417, N802
    """Create the markdown extension.

    Args:
        context: Whether to create full project context. Default: False (fast).
            Set to True for complete project info (expensive but complete).

    Note:
        Context can also be specified per-block:
        /// mknodes | context
        {{ "With full context" | MkHeader(level=2) }}
        ///
    """
    return MkNodesExtension(**kwargs)

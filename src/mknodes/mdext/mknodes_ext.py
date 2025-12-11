"""MkNodes Markdown Extension.

A pymdownx-based block extension that allows rendering Jinja templates
using the MkNodes NodeEnvironment within markdown documents.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Any
import xml.etree.ElementTree as ET

from pymdownx.blocks import BlocksExtension  # type: ignore[import-untyped]
from pymdownx.blocks.block import Block  # type: ignore[import-untyped]
from pymdownx.superfences import fence_code_format  # type: ignore[import-untyped]
import yamling

from mknodes.utils import icons


if TYPE_CHECKING:
    from mknodes.jinja.nodeenvironment import NodeEnvironment


logger = logging.getLogger(__name__)


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

                # Get markdown extensions (from zensical config, mkdocs.yml, or fallback)
                ext_names, ext_configs = _get_markdown_config()

                # Exclude problematic extensions:
                # - mkdocstrings: MkDocs plugin with dict-format extensions that cause errors
                # - mknodes.mdext: our own extension, to prevent recursion
                excluded = {"mkdocstrings", "mknodes.mdext"}
                ext_names = [e for e in ext_names if e not in excluded]
                ext_configs = {k: v for k, v in ext_configs.items() if k not in excluded}

                # Create a markdown instance with the extensions
                md = markdown.Markdown(extensions=ext_names, extension_configs=ext_configs)
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
            # On error, show the error message with the template that failed
            block.clear()
            error_elem = ET.SubElement(block, "div")
            error_elem.set("class", "mknodes-error")
            error_elem.set("style", "color: red; border: 1px solid red; padding: 0.5rem;")

            # Create a more informative error message
            error_msg = f"MkNodes rendering error: {e}\n\nFailed to render:\n{jinja_content}"
            error_elem.text = error_msg


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


def _get_markdown_config() -> tuple[list[str], dict[str, Any]]:
    """Get markdown extensions and configs, trying zensical config first.

    Note: This function is intentionally NOT cached because zensical's config
    may not be available when this module is first imported, but becomes
    available later during the build process.

    Returns:
        Tuple of (extension_names, extension_configs) for markdown.Markdown.
    """
    # Try to get config from zensical if available (already parsed)
    try:
        from zensical.config import get_config  # type: ignore[import-untyped]

        config = get_config()
        if config and "markdown_extensions" in config and "mdx_configs" in config:
            logger.debug("Using zensical parsed config")
            return config["markdown_extensions"], config["mdx_configs"]
    except ImportError:
        pass
    except Exception:  # noqa: BLE001
        logger.debug("Failed to get zensical config")

    # Fallback: load and parse from mkdocs.yml or use defaults
    extensions = _load_markdown_extensions_raw()
    return _parse_extension_configs(extensions)


def _parse_extension_configs(extensions: list[Any]) -> tuple[list[str], dict[str, Any]]:
    """Parse extension list into names and configs for markdown.Markdown.

    Args:
        extensions: List of extension names and/or dicts with configs.

    Returns:
        Tuple of (extension_names, extension_configs) for markdown.Markdown.
    """
    ext_names = []
    ext_configs: dict[str, Any] = {}

    for ext in extensions:
        if isinstance(ext, dict):
            # Dict format: {"extension.name": {"option": value}}
            for ext_name, config in ext.items():
                ext_names.append(ext_name)
                # Ensure config is always a dict, not None
                ext_configs[ext_name] = config if isinstance(config, dict) else {}
        else:
            # String format: "extension.name"
            ext_names.append(ext)

    return ext_names, ext_configs


def _load_markdown_extensions_raw() -> list[Any]:
    """Load markdown extensions from mkdocs.yml or use fallback.

    Attempts to load extensions from mkdocs.yml using unsafe mode.
    Falls back to default extensions with mermaid support if loading fails.

    Returns:
        List of markdown extensions and their configurations (raw format).
    """
    fallback_extensions: list[Any] = [
        "tables",
        "admonition",
        "attr_list",
        "md_in_html",
        "pymdownx.details",
        "pymdownx.mark",
        "pymdownx.snippets",
        "pymdownx.tilde",
        "pymdownx.inlinehilite",
        {
            "pymdownx.emoji": {
                "emoji_index": icons.twemoji,
                "emoji_generator": icons.to_svg,
            }
        },
        {
            "pymdownx.highlight": {
                "pygments_lang_class": True,
            }
        },
        {
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",
                        "class": "mermaid",
                        "format": fence_code_format,
                    }
                ]
            }
        },
        {
            "pymdownx.tabbed": {
                "alternate_style": True,
            }
        },
        {
            "pymdownx.tasklist": {
                "custom_checkbox": True,
            }
        },
        "sane_lists",
    ]

    try:
        # Look for mkdocs.yml in the current directory or parent directories
        current = Path.cwd()
        mkdocs_path = None

        for parent in [current, *current.parents]:
            candidate = parent / "mkdocs.yml"
            if candidate.exists():
                mkdocs_path = candidate
                break

        if not mkdocs_path:
            logger.debug("mkdocs.yml not found, using fallback extensions")
            return fallback_extensions

        # Load mkdocs.yml (yamling uses unsafe mode by default, supporting !!python/name tags)
        config = yamling.load_yaml_file(mkdocs_path)

        if not config or "markdown_extensions" not in config:
            logger.debug("No markdown_extensions in mkdocs.yml, using fallback")
            return fallback_extensions

        extensions = config["markdown_extensions"]
        logger.debug("Loaded %d extensions from mkdocs.yml", len(extensions))
    except Exception:  # noqa: BLE001
        logger.debug("Failed to load mkdocs.yml extensions, using fallback")
        return fallback_extensions
    else:
        return extensions


def makeExtension(**kwargs: Any) -> MkNodesExtension:  # noqa: N802
    """Create the markdown extension.

    Args:
        kwargs: Keyword arguments to pass to the extension.
    """
    return MkNodesExtension(**kwargs)

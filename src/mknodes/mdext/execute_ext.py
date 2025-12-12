"""Python code execution Markdown extension.

A superfences-based extension that executes Python code blocks marked with `exec`
and renders their output as markdown.

Usage:
    ```python exec="true"
    print("# Hello World")
    print("This becomes **markdown**")
    ```

The code is executed and stdout is captured, then rendered as markdown.

Options:
    exec: "true" to enable execution (required)
    session: session name to persist globals between code blocks
    html: "true" to inject output as raw HTML instead of markdown
    source: "above", "below", "tabbed-left", "tabbed-right" to show source code
    result: language to use for formatting result as code block
    title: optional title for the code block
    id: optional ID for the code block
"""

from __future__ import annotations

from collections import defaultdict
from functools import partial
from io import StringIO
import logging
import sys
import traceback
from typing import TYPE_CHECKING, Any

from markdown.extensions import Extension


if TYPE_CHECKING:
    from markdown import Markdown


logger = logging.getLogger(__name__)

# Session storage for persistent globals across code blocks
_sessions: dict[str, dict[str, Any]] = defaultdict(dict)
_counter: int = 0


def _buffer_print(buffer: StringIO, *texts: Any, end: str = "\n", **kwargs: Any) -> None:
    """Print function that writes to a buffer."""
    buffer.write(" ".join(str(text) for text in texts) + end)


def _get_mknodes_namespace() -> dict[str, Any]:
    """Build namespace with mknodes classes and utilities."""
    namespace: dict[str, Any] = {"__name__": "__exec__", "__builtins__": __builtins__}

    import mknodes as mk

    namespace["mk"] = mk
    for name in mk.__all__:
        namespace[name] = getattr(mk, name)
    return namespace


def _run_python(
    code: str,
    *,
    session: str | None = None,
    extra_globals: dict[str, Any] | None = None,
) -> str:
    """Execute Python code and capture stdout.

    Args:
        code: Python code to execute
        session: Optional session name for persistent globals
        extra_globals: Additional globals to inject

    Returns:
        Captured stdout output
    """
    # Get or create session globals
    if session:
        exec_globals = _sessions[session]
        # Initialize with mknodes namespace if empty
        if not exec_globals:
            exec_globals.update(_get_mknodes_namespace())
    else:
        exec_globals = _get_mknodes_namespace()

    # Add extra globals
    if extra_globals:
        exec_globals.update(extra_globals)

    # Capture stdout
    buffer = StringIO()
    exec_globals["print"] = partial(_buffer_print, buffer)

    # Store original stdout for potential direct writes
    old_stdout = sys.stdout
    sys.stdout = buffer

    try:
        compiled = compile(code, filename="<exec>", mode="exec")
        exec(compiled, exec_globals)
    finally:
        sys.stdout = old_stdout

    return buffer.getvalue()


def _format_error(code: str, error: Exception) -> str:
    """Format an execution error as markdown."""
    tb = traceback.format_exc()
    return f"""**Execution Error: {type(error).__name__}**

{error}

```python
{code}
```

```
{tb}
```
"""


def _add_source(
    source: str,
    output: str,
    location: str,
    tabs: tuple[str, str] = ("Source", "Result"),
) -> str:
    """Add source code to output based on location setting."""
    # Filter out lines with "# exec: hide"
    source_lines = [line for line in source.split("\n") if "# exec: hide" not in line]
    source = "\n".join(source_lines).strip()

    source_block = f"```python\n{source}\n```"

    if location == "above":
        return f"{source_block}\n\n{output}"
    if location == "below":
        return f"{output}\n\n{source_block}"
    if location == "tabbed-left":
        return _tabbed((tabs[0], source_block), (tabs[1], output))
    if location == "tabbed-right":
        return _tabbed((tabs[1], output), (tabs[0], source_block))

    return output


def _tabbed(*tabs: tuple[str, str]) -> str:
    """Format content as pymdownx.tabbed tabs."""
    parts = []
    for title, content in tabs:
        parts.append(f'=== "{title}"')
        # Indent content for tab
        indented = "\n".join(f"    {line}" for line in content.split("\n"))
        parts.append(indented)
        parts.append("")
    return "\n".join(parts)


def validator(
    language: str,
    inputs: dict[str, str],
    options: dict[str, Any],
    attrs: dict[str, Any],
    md: Markdown,
) -> bool:
    """Validate code blocks for execution.

    Returns True if this code block should be handled by our formatter.
    """
    # Only handle python/py blocks with exec="true"
    if language not in {"python", "py"}:
        return False

    exec_value = inputs.pop("exec", "").lower()
    if exec_value not in {"true", "1", "yes", "on"}:
        return False

    # Extract our options
    options["session"] = inputs.pop("session", "")
    options["html"] = inputs.pop("html", "").lower() in {"true", "1", "yes", "on"}
    options["source"] = inputs.pop("source", "")
    options["result"] = inputs.pop("result", "")
    options["title"] = inputs.pop("title", "")
    options["id"] = inputs.pop("id", "")
    options["tabs"] = (
        inputs.pop("tab_source", "Source"),
        inputs.pop("tab_result", "Result"),
    )
    # Pass remaining inputs as extra
    options["extra"] = dict(inputs)

    return True


def formatter(
    source: str,
    language: str,
    css_class: str,
    options: dict[str, Any],
    md: Markdown,
    classes: list[str] | None = None,
    id_value: str = "",
    attrs: dict[str, Any] | None = None,
    **kwargs: Any,
) -> str:
    """Execute Python code and return rendered HTML.

    This is called by superfences for code blocks that passed validation.
    """
    global _counter
    _counter += 1

    session = options.get("session") or None
    html_output = options.get("html", False)
    show_source = options.get("source", "")
    result_lang = options.get("result", "")
    tabs = options.get("tabs", ("Source", "Result"))

    try:
        output = _run_python(source, session=session)
    except Exception as e:  # noqa: BLE001
        error_md = _format_error(source, e)
        return md.convert(error_md)

    # Empty output
    if not output.strip() and not show_source:
        return ""

    # Raw HTML output
    if html_output:
        if show_source:
            # Need to convert source block to HTML and combine
            source_html = md.convert(f"```python\n{source}\n```")
            if show_source == "above":
                return f"{source_html}\n{output}"
            if show_source == "below":
                return f"{output}\n{source_html}"
        return output

    # Format result as code block if requested
    if result_lang:
        output = f"```{result_lang}\n{output}\n```"

    # Add source code display
    if show_source:
        output = _add_source(source, output, show_source, tabs)

    # Convert markdown output to HTML.
    # We must use md.htmlStash.store() to inject raw HTML and return a placeholder,
    # because calling md.convert() recursively corrupts superfences state
    # (self.ws becomes None, causing "None" to be prepended to output).
    return _convert_markdown_safe(output, md)


def _convert_markdown_safe(text: str, md: Markdown) -> str:
    """Convert markdown to HTML without corrupting parent markdown state.

    Creates a minimal new Markdown instance for conversion to avoid
    state corruption when called from within a superfences formatter.
    """
    from markdown import Markdown as Md

    # Create minimal markdown instance with just the extensions needed for code blocks
    fresh_md = Md(
        extensions=[
            "tables",
            "pymdownx.superfences",
        ],
        extension_configs={
            "pymdownx.superfences": {
                "custom_fences": [
                    {
                        "name": "mermaid",
                        "class": "mermaid",
                        "format": __import__(
                            "pymdownx.superfences", fromlist=["fence_code_format"]
                        ).fence_code_format,
                    }
                ]
            }
        },
    )
    return fresh_md.convert(text)


class ExecuteExtension(Extension):
    """Markdown extension that registers the execute fence with superfences.

    This extension requires pymdownx.superfences to be loaded.
    It registers a custom fence for python/py code blocks with exec="true".
    """

    def __init__(self, **kwargs: Any) -> None:
        self.config = {
            "auto_register": [
                True,
                "Automatically register with superfences if available",
            ],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md: Markdown) -> None:  # noqa: N802
        """Register the extension with the Markdown instance.

        If superfences is available and auto_register is True,
        we add our custom fence configuration.
        """
        # Store config for later access
        md.registerExtension(self)

        # Try to register with superfences
        if self.getConfig("auto_register"):
            self._register_fence(md)

    def _register_fence(self, md: Markdown) -> None:
        """Register our fence with superfences."""
        # Check if superfences config exists
        if not hasattr(md, "mdx_configs"):
            md.mdx_configs = {}  # type: ignore[attr-defined]

        sf_config = md.mdx_configs.get("pymdownx.superfences", {})  # type: ignore[attr-defined]
        custom_fences = sf_config.setdefault("custom_fences", [])

        # Add our fence if not already present
        fence_names = {f.get("name") for f in custom_fences}
        if "python" not in fence_names:
            custom_fences.append({
                "name": "python",
                "class": "python",
                "validator": validator,
                "format": formatter,
            })
        if "py" not in fence_names:
            custom_fences.append({
                "name": "py",
                "class": "python",
                "validator": validator,
                "format": formatter,
            })

        md.mdx_configs["pymdownx.superfences"] = sf_config  # type: ignore[attr-defined]


def get_custom_fences() -> list[dict[str, Any]]:
    """Get the custom fence configurations for manual registration.

    Use this if you need to manually configure superfences:

        from mknodes.mdext.execute_ext import get_custom_fences

        md = markdown.Markdown(
            extensions=["pymdownx.superfences"],
            extension_configs={
                "pymdownx.superfences": {
                    "custom_fences": get_custom_fences()
                }
            }
        )
    """
    return [
        {
            "name": "python",
            "class": "python",
            "validator": validator,
            "format": formatter,
        },
        {
            "name": "py",
            "class": "python",
            "validator": validator,
            "format": formatter,
        },
    ]


def makeExtension(**kwargs: Any) -> ExecuteExtension:  # noqa: N802
    """Create the extension instance."""
    return ExecuteExtension(**kwargs)


def reset_sessions() -> None:
    """Clear all session state. Useful between builds."""
    global _counter
    _sessions.clear()
    _counter = 0

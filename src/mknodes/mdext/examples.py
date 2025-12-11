"""Comprehensive example demonstrating the MkNodes markdown extension.

This example shows how to use the MkNodes markdown extension to render
Jinja templates containing MkNodes components within markdown documents.
"""

from __future__ import annotations

import markdown


def basic_example():
    """Basic example showing simple MkNodes usage."""
    print("=== Basic Example ===")

    markdown_content = """
# MkNodes Extension Demo

This is a regular markdown paragraph.

/// mknodes
{{ "Welcome to MkNodes!" | MkHeader(level=2) }}
{{ "This text was generated using **MkNodes** via Jinja templating." | MkText }}
///

Back to regular markdown.
"""

    # Create markdown instance with our extension
    from mknodes.mdext import makeMkNodesExtension

    md = markdown.Markdown(extensions=[makeMkNodesExtension()])
    result = md.convert(markdown_content)

    print("Markdown input:")
    print(markdown_content)
    print("\nRendered HTML:")
    print(result)
    print("\n" + "=" * 60 + "\n")


def advanced_components_example():
    """Example showing various MkNodes components."""
    print("=== Advanced Components Example ===")

    markdown_content = """
# Advanced MkNodes Components

## Progress Bar
/// mknodes
{{ 75 | MkProgressBar }}
///

## Admonition
/// mknodes
{{ mk.MkAdmonition(content="This is an **important** info message!", typ="warning", title="Pay Attention") }}
///

## Code Block
/// mknodes
{{ mk.MkCode(content="def hello_world():\\n    print('Hello from MkNodes!')", language="python") }}
///

## Table
/// mknodes
{{ mk.MkTable([
    ["Feature", "Status", "Notes"],
    ["Headers", "✅ Working", "Dynamic generation"],
    ["Tables", "✅ Working", "From Python data"],
    ["Code", "✅ Working", "Syntax highlighting"]
]) }}
///

## List
/// mknodes
{{ mk.MkList([
    "First item",
    "Second item with **bold** text",
    "Third item with `code`"
]) }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    md = markdown.Markdown(extensions=[makeMkNodesExtension()])
    result = md.convert(markdown_content)

    print("Rendered HTML:")
    print(result)
    print("\n" + "=" * 60 + "\n")


def filter_syntax_example():
    """Example showing Jinja filter syntax for MkNodes."""
    print("=== Filter Syntax Example ===")

    markdown_content = """
# Jinja Filter Syntax

MkNodes supports both direct calls and Jinja filters:

## Using Filters
/// mknodes
{{ "Success!" | MkHeader(level=3) }}
{{ "This uses the filter syntax" | MkText }}
{{ 90 | MkProgressBar }}
///

## Mixed Approaches
/// mknodes
{{ mk.MkAdmonition(content="Direct call syntax", typ="info") }}
{{ "Filter syntax for headers" | MkHeader(level=4) }}
{{ mk.MkCode(content="# Both work great!", language="python") }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    md = markdown.Markdown(extensions=[makeMkNodesExtension()])
    result = md.convert(markdown_content)

    print("Rendered HTML:")
    print(result)
    print("\n" + "=" * 60 + "\n")


def nested_content_example():
    """Example showing complex nested content."""
    print("=== Nested Content Example ===")

    markdown_content = """
# Complex Nested Example

/// mknodes
{{ mk.MkAdmonition(
    content=mk.MkText("This admonition contains a ") ~
            mk.MkCode(content="nested code block", language="bash") ~
            mk.MkText(" and more text!"),
    typ="tip",
    title="Pro Tip"
) }}
///

## Data-Driven Content
/// mknodes
{% set features = [
    {"name": "Headers", "status": "Complete"},
    {"name": "Tables", "status": "Complete"},
    {"name": "Code Blocks", "status": "Complete"},
    {"name": "Admonitions", "status": "Complete"}
] %}

{{ "Project Status" | MkHeader(level=3) }}
{{ mk.MkTable([["Feature", "Status"]] + [[f.name, f.status] for f in features]) }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    md = markdown.Markdown(extensions=[makeMkNodesExtension()])
    result = md.convert(markdown_content)

    print("Rendered HTML:")
    print(result)
    print("\n" + "=" * 60 + "\n")


def integration_example():
    """Example showing integration with existing markdown."""
    print("=== Integration Example ===")

    markdown_content = """
# Integration with Regular Markdown

This shows how MkNodes blocks integrate seamlessly with regular markdown.

## Regular Markdown Features

- Standard **bold** and *italic* text
- [Links](https://example.com)
- `inline code`

```python
# Regular code blocks still work
def regular_function():
    return "This is regular markdown"
```

## Dynamic MkNodes Content

/// mknodes
{{ "Dynamic Section" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This section was generated dynamically!", typ="success") }}

{% for i in range(3) %}
{{ ("Item " + (i + 1)|string) | MkText }}
{% endfor %}
///

## Back to Regular Markdown

And we can continue with regular markdown after the MkNodes block.

> This is a regular blockquote
>
> With multiple lines
"""

    from mknodes.mdext import makeMkNodesExtension

    md = markdown.Markdown(extensions=[makeMkNodesExtension(), "fenced_code", "tables"])
    result = md.convert(markdown_content)

    print("Rendered HTML:")
    print(result)
    print("\n" + "=" * 60 + "\n")


def context_modes_example():
    """Example showing different context modes."""
    print("=== Context Modes Example ===")

    markdown_content = """
# Context Mode Comparison

## Full Context (Default - Expensive)
/// mknodes
{{ "Full Context Header" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This uses full context with complete project info", typ="info") }}
///

## Fallback Context (Fast)
/// mknodes
{{ "Fallback Context Header" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This uses minimal context for better performance", typ="success") }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    print("Testing with full context mode (default):")
    md_full = markdown.Markdown(extensions=[makeMkNodesExtension(context_mode="full")])
    md_full.convert(markdown_content)
    print("✅ Full context rendered successfully")

    print("\nTesting with fallback context mode:")
    md_fallback = markdown.Markdown(extensions=[makeMkNodesExtension(context_mode="fallback")])
    md_fallback.convert(markdown_content)
    print("✅ Fallback context rendered successfully")

    print("\nPerformance comparison:")
    print("- Full context: Complete project context (slower initialization)")
    print("- Fallback context: Minimal context (faster initialization)")

    print("\n" + "=" * 60 + "\n")


def usage_instructions():
    """Print usage instructions."""
    print("=== Usage Instructions ===")
    print("""
To use the MkNodes markdown extension:

1. Install the package with the extension
2. Import and use in your markdown processor:

```python
import markdown
from mknodes.mdext import makeExtension

md = markdown.Markdown(extensions=[makeExtension()])
html = md.convert(your_markdown_content)
```

3. In your markdown, use /// mknodes blocks:

```markdown
/// mknodes
{{ "Your Title" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="Your message", typ="info") }}
///
```

Available syntax:
- Filter syntax: {{ "text" | MkComponent }}
- Direct calls: {{ mk.MkComponent(...) }}
- Jinja features: loops, conditions, variables

Supported components include:
- MkHeader, MkText, MkCode, MkAdmonition
- MkTable, MkList, MkProgressBar
- And many more MkNodes components!
""")


if __name__ == "__main__":
    print("MkNodes Markdown Extension Examples")
    print("=" * 50)

    try:
        basic_example()
        advanced_components_example()
        filter_syntax_example()
        nested_content_example()
        integration_example()
        context_modes_example()
        usage_instructions()

        print("✅ All examples completed successfully!")

    except Exception as e:  # noqa: BLE001
        print(f"❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()

"""Example usage for the execute markdown extension.

This module provides examples demonstrating how to use the Python code
execution extension with various configurations.
"""

from __future__ import annotations


# Basic usage - execute Python and render output as markdown
BASIC_EXAMPLE = """
```python exec="true"
print("# Generated Header")
print("")
print("This text was **generated** by Python code!")
```
"""

# Using sessions to persist state between code blocks
SESSION_EXAMPLE = """
```python exec="true" session="demo"
# First block - define variables
counter = 1
data = {"name": "MkNodes"}
print(f"Counter initialized to {counter}")
```

```python exec="true" session="demo"
# Second block - use variables from first block
counter += 1
print(f"Counter is now {counter}")
print(f"Data: {data}")
```
"""

# Show source code alongside output
SOURCE_DISPLAY_EXAMPLE = """
```python exec="true" source="tabbed-left"
items = ["apple", "banana", "cherry"]
print("## Fruit List")
print("")
for item in items:
    print(f"- {item}")
```
"""

# Source above output
SOURCE_ABOVE_EXAMPLE = """
```python exec="true" source="above"
print("**Output appears below the source code**")
```
"""

# Source below output
SOURCE_BELOW_EXAMPLE = """
```python exec="true" source="below"
print("**Output appears above the source code**")
```
"""

# Format output as a specific language code block
RESULT_FORMAT_EXAMPLE = """
```python exec="true" result="json"
import json
data = {"name": "test", "values": [1, 2, 3]}
print(json.dumps(data, indent=2))
```
"""

# Raw HTML output
HTML_OUTPUT_EXAMPLE = """
```python exec="true" html="true"
print('<div style="background: #f0f0f0; padding: 1em; border-radius: 4px;">')
print('<strong>Raw HTML</strong> content here')
print('</div>')
```
"""

# Using mknodes classes
MKNODES_EXAMPLE = """
```python exec="true"
# mknodes classes are available in the namespace
header = MkHeader("Generated with MkNodes", level=2)
print(header)

admonition = MkAdmonition("This is a note!", typ="note", title="Notice")
print(admonition)
```
"""

# Hide specific lines from source display
HIDE_LINES_EXAMPLE = """
```python exec="true" source="above"
import os  # exec: hide
SECRET = os.environ.get("SECRET", "default")  # exec: hide

# This line is visible
print(f"Processing with configured settings...")
print("## Result")
print("Operation completed successfully!")
```
"""

# Custom tab titles
CUSTOM_TABS_EXAMPLE = """
```python exec="true" source="tabbed-left" tab_source="Code" tab_result="Output"
print("# Custom Tab Titles")
print("")
print("The tabs above have custom names!")
```
"""


def get_example_markdown() -> str:
    """Return a complete markdown document with all examples."""
    return f"""# Execute Extension Examples

## Basic Usage

Execute Python code and render the output as markdown:

{BASIC_EXAMPLE}

## Sessions

Use sessions to persist state between code blocks:

{SESSION_EXAMPLE}

## Showing Source Code

### Tabbed Display

{SOURCE_DISPLAY_EXAMPLE}

### Source Above

{SOURCE_ABOVE_EXAMPLE}

### Source Below

{SOURCE_BELOW_EXAMPLE}

### Custom Tab Titles

{CUSTOM_TABS_EXAMPLE}

## Result Formatting

Format output as a specific code block language:

{RESULT_FORMAT_EXAMPLE}

## Raw HTML Output

Output raw HTML directly:

{HTML_OUTPUT_EXAMPLE}

## MkNodes Integration

Use mknodes classes directly:

{MKNODES_EXAMPLE}

## Hiding Lines

Hide implementation details from displayed source:

{HIDE_LINES_EXAMPLE}
"""


def get_mkdocs_config_example() -> str:
    """Return example mkdocs.yml configuration."""
    return """# mkdocs.yml configuration for execute extension
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: python
          class: python
          validator: !!python/name:mknodes.mdext.execute_ext.validator
          format: !!python/name:mknodes.mdext.execute_ext.formatter
        - name: py
          class: python
          validator: !!python/name:mknodes.mdext.execute_ext.validator
          format: !!python/name:mknodes.mdext.execute_ext.formatter
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
  - pymdownx.tabbed:
      alternate_style: true
  - admonition
"""


def get_programmatic_example() -> str:
    """Return example of programmatic usage."""
    return '''
from markdown import Markdown
from mknodes.mdext.execute_ext import get_custom_fences

# Create markdown instance with execute extension
md = Markdown(
    extensions=["pymdownx.superfences", "pymdownx.tabbed", "admonition"],
    extension_configs={
        "pymdownx.superfences": {
            "custom_fences": get_custom_fences()
        },
        "pymdownx.tabbed": {
            "alternate_style": True
        }
    }
)

# Convert markdown with executable code blocks
source = """
```python exec="true"
print("# Hello from Python!")
print("")
print("This was executed at build time.")
```
"""

html = md.convert(source)
print(html)
'''


if __name__ == "__main__":
    print("=" * 60)
    print("EXAMPLE MARKDOWN DOCUMENT")
    print("=" * 60)
    print(get_example_markdown())
    print()
    print("=" * 60)
    print("MKDOCS.YML CONFIGURATION")
    print("=" * 60)
    print(get_mkdocs_config_example())
    print()
    print("=" * 60)
    print("PROGRAMMATIC USAGE")
    print("=" * 60)
    print(get_programmatic_example())

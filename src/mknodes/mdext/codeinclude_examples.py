"""Examples demonstrating the CodeInclude markdown extension.

This extension automatically wraps included files in fenced code blocks
with syntax highlighting and filename as title.
"""

from __future__ import annotations

from pathlib import Path
import tempfile

import markdown


def basic_file_include_example():
    """Basic example showing file inclusion with automatic code block wrapping."""
    print("=== Basic File Include Example ===")

    # Create a temporary Python file
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = Path(tmpdir) / "example.py"
        test_file.write_text("""def hello_world():
    \"\"\"A simple greeting function.\"\"\"
    return "Hello, World!"

if __name__ == "__main__":
    print(hello_world())
""")

        markdown_content = f"""
# Code Include Demo

Here's a Python file automatically wrapped in a code block:

@@@codeinclude "{test_file.name}"

The file is automatically wrapped with syntax highlighting and title!
"""

        from mknodes.mdext import makeCodeIncludeExtension

        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(markdown_content)

        print("Markdown input:")
        print(markdown_content)
        print("\nRendered HTML:")
        print(result)
        print("\n" + "=" * 60 + "\n")


def multiple_files_example():
    """Example showing multiple file includes with different languages."""
    print("=== Multiple Files Example ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create various file types
        py_file = Path(tmpdir) / "script.py"
        py_file.write_text('print("Python code")')

        js_file = Path(tmpdir) / "script.js"
        js_file.write_text('console.log("JavaScript code");')

        yaml_file = Path(tmpdir) / "config.yml"
        yaml_file.write_text(
            """
name: example
version: 1.0.0
settings:
  debug: true
""".strip()
        )

        markdown_content = """
# Multiple File Types

## Python Script
@@@codeinclude "script.py"

## JavaScript
@@@codeinclude "script.js"

## YAML Configuration
@@@codeinclude "config.yml"
"""

        from mknodes.mdext import makeCodeIncludeExtension

        md = markdown.Markdown(
            extensions=["fenced_code", makeCodeIncludeExtension(base_path=[tmpdir])]
        )
        result = md.convert(markdown_content)

        print("Rendered HTML:")
        print(result)
        print("\n" + "=" * 60 + "\n")


def language_detection_example():
    """Example showing automatic language detection from extensions."""
    print("=== Language Detection Example ===")

    extensions = {
        "example.py": "python",
        "example.js": "javascript",
        "example.ts": "typescript",
        "example.rs": "rust",
        "example.go": "go",
        "example.java": "java",
        "example.cpp": "cpp",
        "example.rb": "ruby",
        "example.sh": "bash",
        "example.sql": "sql",
        "example.html": "html",
        "example.css": "css",
        "example.json": "json",
        "example.yaml": "yaml",
        "example.toml": "toml",
        "example.md": "markdown",
    }

    print("Supported file extensions and their detected languages:")
    for filename, lang in extensions.items():
        print(f"  {filename:20} -> {lang}")

    print("\nAll these files will be automatically wrapped with correct syntax highlighting!")
    print("\n" + "=" * 60 + "\n")


def integration_with_regular_markdown():
    """Example showing integration with standard markdown."""
    print("=== Integration with Regular Markdown ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        code_file = Path(tmpdir) / "utils.py"
        code_file.write_text("""def calculate_sum(numbers):
    return sum(numbers)

def calculate_average(numbers):
    return sum(numbers) / len(numbers) if numbers else 0
""")

        markdown_content = """
# Documentation with Code Includes

This is a regular markdown document that seamlessly integrates
code includes.

## Overview

Here are some utility functions:

@@@codeinclude "utils.py"

## Usage

You can call these functions like this:

```python
result = calculate_sum([1, 2, 3, 4, 5])
print(f"Sum: {result}")
```

The included file above is **automatically wrapped** in a code block
with the correct language and filename as title!
"""

        from mknodes.mdext import makeCodeIncludeExtension

        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                makeCodeIncludeExtension(base_path=[tmpdir]),
                "tables",
            ]
        )
        result = md.convert(markdown_content)

        print("Rendered HTML:")
        print(result)
        print("\n" + "=" * 60 + "\n")


def upath_support_example():
    """Example showing UPath support for URLs and various protocols."""
    print("=== UPath Support Example ===")

    markdown_content = """
# Remote File Include

This can include files from various sources via UPath:

@@@codeinclude "https://raw.githubusercontent.com/example/repo/main/README.md"

@@@codeinclude "s3://bucket/path/to/file.py"

@@@codeinclude "gs://bucket/path/to/file.py"
"""

    print("Markdown content:")
    print(markdown_content)

    print("\nNote: UPath automatically handles URLs and cloud storage!")
    print("Supported protocols: http, https, s3, gs, gcs, azure, and more")
    print("\n" + "=" * 60 + "\n")


def configuration_options_example():
    """Example showing configuration options."""
    print("=== Configuration Options ===")

    print("""
Available configuration options:

1. base_path: Base directory for file resolution
   makeCodeIncludeExtension(base_path=["/path/to/files"])

2. check_paths: Fail build if file not found
   makeCodeIncludeExtension(check_paths=True)

Example usage:
```python
from mknodes.mdext import makeCodeIncludeExtension
import markdown

md = markdown.Markdown(
    extensions=[
        "fenced_code",  # Required for code block rendering
        makeCodeIncludeExtension(
            base_path=["./examples", "./src"],
            check_paths=True
        )
    ]
)
```

Minimal configuration (defaults):
```python
md = markdown.Markdown(
    extensions=[
        "fenced_code",
        makeCodeIncludeExtension()
    ]
)
```
""")
    print("\n" + "=" * 60 + "\n")


def comparison_with_snippets():
    """Compare with standard snippets extension."""
    print("=== Comparison with pymdownx.snippets ===")

    print("""
**pymdownx.snippets:**
Includes file content directly into markdown for further processing.

Input:
    --8<-- "file.py"

Output:
    <raw file content inserted here>


**mknodes.mdext.codeinclude:**
Wraps file content in a fenced code block with syntax highlighting and title.

Input:
    @@@codeinclude "file.py"

Output:
    ```python title="file.py"
    <file content>
    ```


**Key Differences:**

1. Syntax: snippets uses --8<--, codeinclude uses @@@codeinclude
2. Purpose: snippets for including markdown, codeinclude for displaying code
3. Output: snippets inserts raw content, codeinclude wraps in code blocks
4. Features: snippets has line selection/sections, codeinclude is simpler


**When to use each:**

- Use **snippets**: When you want to include markdown content or text
  that should be processed further (e.g., including partial markdown files)

- Use **codeinclude**: When you want to show code examples from files
  with automatic syntax highlighting and filename display
""")
    print("\n" + "=" * 60 + "\n")


def usage_in_mkdocs():
    """Show how to use in mkdocs.yml."""
    print("=== Usage in MkDocs ===")

    print("""
Add to your mkdocs.yml:

```yaml
markdown_extensions:
  - pymdownx.superfences  # Required for code blocks
  - mknodes.mdext.codeinclude:
      base_path:
        - docs/examples
        - src
      check_paths: true
```

Then in your markdown files:

```markdown
# My Documentation

## Example Implementation

@@@codeinclude "myapp/main.py"

The code above shows the main entry point.
```

This will render as:

```python title="main.py"
<content of myapp/main.py>
```

**Note:** Make sure pymdownx.superfences or fenced_code is enabled
for proper code block rendering!
""")
    print("\n" + "=" * 60 + "\n")


def absolute_and_relative_paths():
    """Example showing absolute and relative path handling."""
    print("=== Absolute and Relative Paths ===")

    with tempfile.TemporaryDirectory() as tmpdir:
        # Create nested structure
        subdir = Path(tmpdir) / "src" / "app"
        subdir.mkdir(parents=True)

        main_file = subdir / "main.py"
        main_file.write_text("# main module")

        # Absolute path
        abs_path = str(main_file.resolve())
        md_content1 = f'@@@codeinclude "{abs_path}"'

        # Relative path
        md_content2 = '@@@codeinclude "src/app/main.py"'

        from mknodes.mdext import makeCodeIncludeExtension

        md = markdown.Markdown(
            extensions=[
                "fenced_code",
                makeCodeIncludeExtension(base_path=[tmpdir]),
            ]
        )

        print("Absolute path example:")
        print(f"  {md_content1}")
        result1 = md.convert(md_content1)
        print(f"  ✅ Rendered: {len(result1)} chars")

        print("\nRelative path example:")
        print(f"  {md_content2}")
        result2 = md.convert(md_content2)
        print(f"  ✅ Rendered: {len(result2)} chars")

        print("\nBoth absolute and relative paths work!")
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    print("CodeInclude Markdown Extension Examples")
    print("=" * 50)

    try:
        basic_file_include_example()
        multiple_files_example()
        language_detection_example()
        integration_with_regular_markdown()
        upath_support_example()
        configuration_options_example()
        comparison_with_snippets()
        usage_in_mkdocs()
        absolute_and_relative_paths()

        print("✅ All examples completed successfully!")

    except Exception as e:  # noqa: BLE001
        print(f"❌ Error running examples: {e}")
        import traceback

        traceback.print_exc()

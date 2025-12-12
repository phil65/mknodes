# CodeInclude Extension

A minimalist markdown extension for including code files with automatic syntax highlighting.

## Quick Start

```yaml
# mkdocs.yml
markdown_extensions:
  - pymdownx.superfences  # Required
  - mknodes.mdext.codeinclude:
      base_path: [docs, src]
      check_paths: true
```

```markdown
# Documentation

@@@codeinclude "path/to/file.py"
```

Renders as:

````markdown
```python title="file.py"
<file content>
```
````

## Features

- 🎨 **Automatic syntax highlighting** from 40+ file extensions
- 📦 **UPath support** for local files, URLs, and cloud storage (s3, gcs, azure)
- 🏷️ **Filename titles** automatically added to code blocks
- ⚡ **Simple configuration** with just 2 options
- 🔒 **Safe by default** with optional strict path checking

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `base_path` | `["."]` | Search paths for files |
| `check_paths` | `False` | Fail on missing files |

## Syntax

```markdown
@@@codeinclude "relative/path/to/file.ext"
@@@codeinclude "/absolute/path/to/file.ext"
@@@codeinclude "https://example.com/file.ext"
@@@codeinclude "s3://bucket/file.ext"
```

## Why Not pymdownx.snippets?

- **Different syntax** (`@@@codeinclude` vs `--8<--`)
- **Auto wrapping** in code blocks with syntax highlighting
- **Simpler** - no line selection, no sections, just show the file
- **UPath integration** - works with URLs and cloud storage out of the box

Use `pymdownx.snippets` when you need to include markdown content or need line/section selection.
Use `codeinclude` when you want to display code files with syntax highlighting.

## Implementation

Built with:
- **UPath** for flexible file system access
- **Minimal dependencies** (just base_path and check_paths)
- **Markdown preprocessor** at priority 32
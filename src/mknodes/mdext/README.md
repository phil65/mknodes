# MkNodes Markdown Extensions

A collection of markdown extensions for MkNodes, including dynamic content rendering and code file inclusion.

## Overview

The MkNodes markdown extension enables you to embed dynamic content generation directly in your markdown files using the `/// mknodes` block syntax.

## Installation

The extension is included with the MkNodes package:

```bash
pip install mknodes
```

## Quick Start

### MkDocs Configuration

```yaml
# mkdocs.yml
markdown_extensions:
  - mknodes.mdext
```

### Markdown Usage

```markdown
# My Document

/// mknodes
{{ "Dynamic Header" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="Generated content!", typ="info") }}
{{ 75 | MkProgressBar }}
///
```

## Configuration

### The `context` Option

The extension has a single boolean option `context` that controls whether to create a full project context:

| Setting | Performance | Use Case |
|---------|-------------|----------|
| `context: false` (default) | **~50x faster** | Most use cases, simple content |
| `context: true` | Slower | When you need full project metadata |

#### MkDocs Configuration

```yaml
# Default - no context (fast)
markdown_extensions:
  - mknodes.mdext

# With full context (when needed)
markdown_extensions:
  - mknodes.mdext:
      context: true
```

#### Programmatic Configuration

```python
import markdown
from mknodes.mdext import makeExtension

# Default (fast)
md = markdown.Markdown(extensions=[makeExtension()])

# With full context
md = markdown.Markdown(extensions=[makeExtension(context=True)])
```

### Per-Block Context

You can enable full context for specific blocks using the `| context` argument:

```markdown
## Fast content (default)
/// mknodes
{{ "Quick render" | MkHeader(level=2) }}
///

## Content needing full context
/// mknodes | context
{{ "With project metadata" | MkHeader(level=2) }}
///
```

## Syntax

### Filter Syntax

```markdown
/// mknodes
{{ "Title" | MkHeader(level=2) }}
{{ "Some text" | MkText }}
{{ 85 | MkProgressBar }}
///
```

### Direct Calls

```markdown
/// mknodes
{{ mk.MkAdmonition(content="Important!", typ="warning") }}
{{ mk.MkCode(content="print('hello')", language="python") }}
{{ mk.MkTable([["Name", "Value"], ["foo", "bar"]]) }}
///
```

### Jinja Features

```markdown
/// mknodes
{% for i in range(3) %}
{{ ("Item " ~ (i + 1)) | MkText }}
{% endfor %}
///
```

## Available Components

All MkNodes components are available:

- **Text**: `MkText`, `MkHeader`
- **Code**: `MkCode` (with syntax highlighting)
- **Admonitions**: `MkAdmonition` (info, warning, error, success, etc.)
- **Data**: `MkTable`, `MkList`, `MkDefinitionList`
- **Interactive**: `MkProgressBar`, `MkTabs`, `MkDetails`
- **And many more...**

## Performance

The default `context=false` setting is approximately **50x faster** than `context=true`:

| Setting | Typical Render Time |
|---------|---------------------|
| `context=false` | ~0.04s |
| `context=true` | ~2.0s |

**Recommendation**: Use the default (`context=false`) unless you specifically need project metadata.

## Examples

### Basic Content

```markdown
/// mknodes
{{ "Welcome" | MkHeader(level=1) }}
{{ mk.MkAdmonition(content="Hello World!", typ="success") }}
///
```

### Tables

```markdown
/// mknodes
{{ mk.MkTable([
    ["Feature", "Status"],
    ["Headers", "✅"],
    ["Tables", "✅"],
    ["Code", "✅"]
]) }}
///
```

### Code Blocks

```markdown
/// mknodes
{{ mk.MkCode(content="def hello():\n    return 'world'", language="python") }}
///
```

### Progress Indicators

```markdown
/// mknodes
{{ "Completion: " | MkText }}{{ 100 | MkProgressBar }}
{{ "In Progress: " | MkText }}{{ 60 | MkProgressBar }}
///
```

## Integration with Other Extensions

```yaml
markdown_extensions:
  - mknodes.mdext
  - admonition
  - pymdownx.superfences
  - pymdownx.highlight
  - tables
```

## Error Handling

When a template fails, a visible error is displayed:

```html
<div class="mknodes-error">
MkNodes rendering error: [error message]
</div>
```

## Troubleshooting

### Block not recognized

Ensure proper spacing around the block:

```markdown
Regular paragraph.

/// mknodes
{{ "Content" | MkHeader }}
///

Another paragraph.
```

### Component errors

Check parameter names match the component's constructor:

```markdown
/// mknodes
{{ mk.MkCode(content="code here", language="python") }}
///
```

### Performance issues

Use the default `context=false` setting. Only use `context=true` or `| context` when you specifically need project metadata.

---

# Code Include Extension

A markdown extension that automatically wraps included files in fenced code blocks with syntax highlighting and filename titles.

## Overview

The Code Include extension automatically wraps included file content in fenced code blocks with proper syntax highlighting and the filename as title. It uses UPath for flexible file access including URLs and cloud storage.

## Installation

Included with MkNodes:

```bash
pip install mknodes
```

## Quick Start

### MkDocs Configuration

```yaml
# mkdocs.yml
markdown_extensions:
  - mknodes.mdext.codeinclude:
      base_path:
        - docs/examples
        - src
```

### Markdown Usage

```markdown
# Documentation

Include a Python file:

@@@codeinclude "myapp/main.py"

The file is automatically wrapped with syntax highlighting!
```

This renders as:

````markdown
```python title="main.py"
<content of myapp/main.py>
```
````

## Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `base_path` | list[str] | `["."]` | Base directories for file resolution |
| `check_paths` | bool | `False` | Fail build if file not found |

### Example Configuration

```yaml
markdown_extensions:
  - pymdownx.superfences  # Required for code block rendering
  - mknodes.mdext.codeinclude:
      base_path:
        - docs/examples
        - src
      check_paths: true
```

## Supported Languages

The extension automatically detects language from file extensions:

| Extension | Language | Extension | Language |
|-----------|----------|-----------|----------|
| `.py` | python | `.js` | javascript |
| `.ts` | typescript | `.jsx` | jsx |
| `.java` | java | `.c`, `.h` | c |
| `.cpp`, `.cc` | cpp | `.cs` | csharp |
| `.go` | go | `.rs` | rust |
| `.rb` | ruby | `.php` | php |
| `.sh`, `.bash` | bash | `.sql` | sql |
| `.html`, `.htm` | html | `.css` | css |
| `.json` | json | `.yaml`, `.yml` | yaml |
| `.toml` | toml | `.md` | markdown |

And many more...

## Usage Examples

### Single File

```markdown
# My Documentation

@@@codeinclude "examples/hello.py"
```

Renders as:

````markdown
```python title="hello.py"
def hello():
    return "Hello, World!"
```
````

### Multiple Files

```markdown
# API Documentation

## Python Implementation
@@@codeinclude "api/handler.py"

## Configuration
@@@codeinclude "config/settings.yaml"

## Tests
@@@codeinclude "tests/test_api.py"
```

### With Regular Markdown

```markdown
# Documentation

Regular markdown content here.

## Code Example

@@@codeinclude "examples/demo.py"

You can continue with regular markdown after the include.
```

## Comparison with pymdownx.snippets

| Feature | pymdownx.snippets | codeinclude |
|---------|------------------|-------------|
| **Syntax** | `--8<-- "file.py"` | `@@@codeinclude "file.py"` |
| **Purpose** | Include raw content for processing | Show code with syntax highlighting |
| **Output** | Raw file content | Fenced code block with language and title |
| **Line selection** | ✅ Supported | ❌ Not supported |
| **Sections** | ✅ Supported | ❌ Not supported |
| **Best for** | Including markdown partials | Displaying code examples |

### When to Use Each

**Use `pymdownx.snippets`:**
- Including markdown content to be processed
- Embedding reusable text snippets
- Need line/section selection

**Use `codeinclude`:**
- Showing code examples from files
- Want automatic syntax highlighting
- Need filename display in title

## UPath Support

The extension uses UPath which supports various file systems and protocols out of the box:

**Local files:**
```markdown
@@@codeinclude "path/to/file.py"
@@@codeinclude "/absolute/path/to/file.py"
```

**URLs:**
```markdown
@@@codeinclude "https://raw.githubusercontent.com/user/repo/main/example.py"
```

**Cloud storage (requires appropriate UPath extras):**
```markdown
@@@codeinclude "s3://bucket/path/to/file.py"
@@@codeinclude "gs://bucket/path/to/file.py"
@@@codeinclude "azure://container/path/to/file.py"
```

Note: Cloud storage and HTTP access may require additional dependencies (e.g., `s3fs`, `gcsfs`, `aiohttp`).

## Programmatic Usage

```python
import markdown
from mknodes.mdext import makeCodeIncludeExtension

md = markdown.Markdown(
    extensions=[
        "fenced_code",
        makeCodeIncludeExtension(
            base_path=["./examples", "./src"],
            check_paths=True
        )
    ]
)

result = md.convert(your_markdown_content)
```

## Error Handling

### Missing Files

With `check_paths=False` (default):
- Missing files are silently ignored
- Build continues without error

With `check_paths=True`:
- Missing files raise `CodeIncludeError`
- Build fails with error message

## License

Part of the MkNodes project.
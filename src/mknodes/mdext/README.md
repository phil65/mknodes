# MkNodes Markdown Extension

A markdown extension that allows rendering Jinja templates using MkNodes components within markdown documents.

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

## License

Part of the MkNodes project.
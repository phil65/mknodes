# MkNodes Markdown Extension

A powerful markdown extension that allows you to use MkNodes components within markdown documents via Jinja templating.

## Overview

The MkNodes markdown extension enables you to embed dynamic content generation directly in your markdown files. It uses pymdownx blocks syntax with Jinja templating to render MkNodes components, giving you programmatic control over your markdown content.

## Installation

The extension is included with the MkNodes package:

```bash
pip install mknodes
```

## Usage

### Basic Setup

```python
import markdown
from mknodes.mdext import makeExtension

# Create markdown processor with MkNodes extension
md = markdown.Markdown(extensions=[makeExtension()])

# Convert markdown with MkNodes blocks
html = md.convert(your_markdown_content)
```

### MkDocs Configuration

The recommended way to configure the extension is via `mkdocs.yml`:

```yaml
# mkdocs.yml
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback  # or "full"
```

**Context modes:**
- `fallback`: Fast initialization, basic functionality (recommended for production)
- `full`: Complete project context, all features (default, good for development)

### Per-Block Configuration

You can also specify context mode per block for fine-grained control:

```markdown
# Uses global configuration
/// mknodes
{{ "Default mode" | MkHeader(level=2) }}
///

# Force fallback mode for this block
/// mknodes | fallback
{{ "Fast rendering" | MkHeader(level=2) }}
///

# Force full context for this block  
/// mknodes | full
{{ "Complete features" | MkHeader(level=2) }}
///
```

#### Context Mode Comparison

| Mode | Performance | Functionality | Use Case |
|------|-------------|---------------|----------|
| `full` | Slower initialization | Complete project context | Development, full features needed |
| `fallback` | Fast initialization | Basic components only | Production, high-frequency rendering |

**When to use `full` context:**
- Development environments
- When you need complete project information
- Complex content generation with metadata
- Full MkNodes feature set required

**When to use `fallback` context:**
- Production web servers
- CI/CD pipelines
- High-frequency rendering
- Simple content generation
- Performance-critical applications

**Per-block context modes:**
Use `/// mknodes | fallback` or `/// mknodes | full` to override the global setting for specific blocks. Aliases: `fast`/`minimal` for fallback, `complete`/`rich` for full.

### Markdown Syntax

Use `/// mknodes` blocks to embed Jinja templates that generate MkNodes components:

```markdown
# Your Document

Regular markdown content here.

/// mknodes
{{ "Dynamic Header" | MkHeader(level=2) }}
{{ "This content was generated dynamically!" | MkText }}
{{ 75 | MkProgressBar }}
///

Back to regular markdown.
```

## Syntax Options

### Filter Syntax
Use Jinja filters for simple component creation:

```markdown
/// mknodes
{{ "Welcome!" | MkHeader(level=1) }}
{{ "Success rate" | MkText }}
{{ 85 | MkProgressBar }}
///
```

### Direct Calls
Use the `mk` namespace for direct component instantiation:

```markdown
/// mknodes
{{ mk.MkAdmonition(content="Important information", typ="warning") }}
{{ mk.MkCode(content="print('Hello World!')", language="python") }}
{{ mk.MkTable([["Name", "Value"], ["foo", "bar"], ["baz", "qux"]]) }}
///
```

### Mixed Approach
Combine both syntaxes as needed:

```markdown
/// mknodes
{{ "Section Title" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="This combines both approaches", typ="info") }}
{{ 90 | MkProgressBar }}
///
```

## Supported Components

All MkNodes components are available within the Jinja environment:

- **Text & Headers**: `MkText`, `MkHeader`
- **Code**: `MkCode` (with syntax highlighting)
- **Admonitions**: `MkAdmonition` (info, warning, error, success, etc.)
- **Data**: `MkTable`, `MkList`, `MkDefinitionList`
- **Interactive**: `MkProgressBar`, `MkTabs`, `MkDetails`
- **Media**: `MkImage`, `MkIcon`
- **Containers**: `MkContainer`, `MkCard`
- **And many more...**

## Configuration Options

### MkDocs Configuration (Recommended)

```yaml
# mkdocs.yml
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback  # or "full"
  - admonition
  - pymdownx.superfences
  - tables
```

### Programmatic Configuration

```python
md = markdown.Markdown(extensions=[
    makeExtension(
        context_mode="fallback",  # or "full"
    )
])
```

### Per-Block Configuration

```markdown
/// mknodes | fallback
{{ "This block uses fallback context" | MkText }}
///

/// mknodes | full
{{ "This block uses full context" | MkText }}
///
```

### Available Options

- **`context_mode`** (default: `"full"`):
  - `"full"`: Complete project context with all features (slower)
  - `"fallback"`: Minimal context for better performance (faster)
- **Per-block arguments**: `fallback`, `full`, `fast`, `minimal`, `complete`, `rich`

## Performance Considerations

### Benchmarking

Run the performance test to see the difference on your system:

```bash
python -m mknodes.mdext.performance_test
```

### Typical Performance Impact

- **Full context**: 2-10x slower initialization, complete functionality
- **Fallback context**: Fast initialization, basic components work

### Optimization Tips

1. **Use fallback context** for production environments
2. **Cache markdown processors** instead of creating new ones
3. **Profile your specific use case** to choose the right mode
4. **Consider context switching** based on content complexity

## Examples

### Simple Content Generation

```markdown
/// mknodes
{{ "Project Status" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="All systems operational!", typ="success") }}
///
```

### Data-Driven Content

```markdown
/// mknodes
{% set data = [["Feature", "Status"], ["Auth", "✅"], ["API", "✅"], ["UI", "🚧"]] %}
{{ "Current Status" | MkHeader(level=2) }}
{{ mk.MkTable(data) }}
///
```

### Code Documentation

```markdown
/// mknodes
{{ "Example Code" | MkHeader(level=3) }}
{{ mk.MkCode(content="def hello():\n    return 'Hello, World!'", language="python") }}
{{ mk.MkAdmonition(content="This function returns a greeting", typ="info") }}
///
```

### Progress Indicators

```markdown
/// mknodes
{{ "Build Progress" | MkHeader(level=2) }}
{{ "Compilation: " | MkText }}{{ 100 | MkProgressBar }}
{{ "Testing: " | MkText }}{{ 75 | MkProgressBar }}
{{ "Deployment: " | MkText }}{{ 25 | MkProgressBar }}
///
```

## Features

- **Seamless Integration**: Works alongside regular markdown content
- **Full Jinja Support**: Use variables, loops, conditions, and filters
- **Rich Components**: Access to all MkNodes components
- **Proper Rendering**: Automatically handles markdown extensions (admonitions, code highlighting, tables, etc.)
- **Error Handling**: Graceful error display when templates fail
- **Performance Options**: Choose between full functionality or fast rendering
- **Context Caching**: Efficient rendering with component caching

## Advanced Usage

### Using Jinja Features

```markdown
/// mknodes
{% set progress_items = [
    {"name": "Setup", "progress": 100},
    {"name": "Development", "progress": 75},
    {"name": "Testing", "progress": 50}
] %}

{{ "Project Progress" | MkHeader(level=2) }}

{% for item in progress_items %}
{{ item.name + ":" | MkText }}
{{ item.progress | MkProgressBar }}
{% endfor %}
///
```

### Conditional Content

```markdown
/// mknodes
{% set is_production = true %}

{% if is_production %}
{{ mk.MkAdmonition(content="Production environment active", typ="warning") }}
{% else %}
{{ mk.MkAdmonition(content="Development environment active", typ="info") }}
{% endif %}
///
```

## Integration with Other Extensions

The MkNodes extension works well with other markdown extensions:

**MkDocs configuration:**
```yaml
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback
  - pymdownx.superfences
  - pymdownx.tabbed
  - admonition
  - tables
  - toc
```

**Programmatic configuration:**
```python
md = markdown.Markdown(extensions=[
    makeExtension(context_mode="fallback"),  # MkNodes extension
    'pymdownx.superfences',    # Enhanced code blocks
    'pymdownx.tabbed',         # Tabbed content
    'admonition',              # Admonitions
    'tables',                  # Table support
    'toc',                     # Table of contents
])
```

## Error Handling

When a template fails to render, the extension displays a clear error message:

```html
<div class="mknodes-error" style="color: red; border: 1px solid red; padding: 0.5rem;">
MkNodes rendering error: [specific error message]
</div>
```

## Component Parameters

Each MkNodes component has specific parameters. Common patterns:

- **MkHeader**: `{{ "Title" | MkHeader(level=2) }}`
- **MkText**: `{{ "Content with **markdown**" | MkText }}`
- **MkCode**: `{{ mk.MkCode(content="code here", language="python") }}`
- **MkAdmonition**: `{{ mk.MkAdmonition(content="message", typ="info", title="Optional") }}`
- **MkTable**: `{{ mk.MkTable([["Col1", "Col2"], ["row1", "row2"]]) }}`
- **MkList**: `{{ mk.MkList(["item1", "item2", "item3"]) }}`
- **MkProgressBar**: `{{ 75 | MkProgressBar }}`

## Best Practices

1. **Configure via mkdocs.yml**: Use YAML configuration instead of programmatic setup
2. **Choose the right context mode**: Use fallback for performance, full for features
3. **Use per-block overrides**: Mix context modes for optimal performance
4. **Keep templates simple**: Complex logic should be in your Python code, not templates
5. **Use meaningful variable names**: Makes templates more readable
6. **Handle errors gracefully**: Test templates before deployment
7. **Combine with regular markdown**: Use MkNodes blocks for dynamic content only
8. **Leverage Jinja features**: Use loops, conditions, and filters for powerful templating
9. **Cache markdown processors**: Don't create new instances for every conversion
10. **Profile your use case**: Measure performance with your actual content

## Troubleshooting

### Common Issues

1. **Component not found**: Ensure the component name is correct and available in MkNodes
2. **Parameter errors**: Check component documentation for correct parameter names
3. **Template syntax errors**: Verify Jinja syntax is correct
4. **Missing dependencies**: Ensure required markdown extensions are installed
5. **Performance issues**: Consider switching to fallback context mode

### Context Mode Issues

- **Full context fails**: May indicate project context issues, try fallback mode
- **Fallback context limited**: Some features need full context, switch if needed
- **Slow performance**: Use fallback context for better speed

### Debug Mode

Enable debugging by catching exceptions:

```python
try:
    html = md.convert(markdown_content)
except Exception as e:
    print(f"Rendering error: {e}")
```

## Migration Guide

### From Previous Versions

If upgrading from a version without context modes:

**Old mkdocs.yml:**
```yaml
markdown_extensions:
  - mknodes.mdext
```

**New mkdocs.yml (recommended):**
```yaml
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback  # or "full"
```

**Programmatic migration:**
```python
# Old way (still works - defaults to full context)
md = markdown.Markdown(extensions=[makeExtension()])

# New way with explicit context mode
md = markdown.Markdown(extensions=[makeExtension(context_mode="full")])

# New optimized way
md = markdown.Markdown(extensions=[makeExtension(context_mode="fallback")])
```

## License

This extension is part of the MkNodes project and follows the same license terms.
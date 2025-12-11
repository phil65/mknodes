"""Configuration examples for MkNodes markdown extension.

This file demonstrates the different ways to configure the context option
for the MkNodes extension, both globally via mkdocs.yml and per-block.
"""

from __future__ import annotations

import markdown


def mkdocs_yml_examples():
    """Show how to configure the extension in mkdocs.yml."""
    print("=== MkDocs YAML Configuration Examples ===")
    print("""
# mkdocs.yml - Default (no context, fast)
markdown_extensions:
  - mknodes.mdext

# mkdocs.yml - With full context (expensive)
markdown_extensions:
  - mknodes.mdext:
      context: true

# mkdocs.yml - Explicit no context (default behavior)
markdown_extensions:
  - mknodes.mdext:
      context: false

# mkdocs.yml - Combined with other extensions
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - pymdownx.tabbed
  - tables
  - mknodes.mdext:
      context: false  # Fast rendering (default)
""")


def per_block_examples():
    """Demonstrate per-block context mode configuration."""
    print("=== Per-Block Configuration Examples ===")

    # Example markdown with different block modes
    markdown_content = """
# Per-Block Context Demo

## Default Mode (uses global config)
/// mknodes
{{ "Default" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="Uses the globally configured context setting", typ="info") }}
///

## No Context (fast, default)
/// mknodes
{{ "Fast Rendering" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This block uses no context for speed", typ="success") }}
{{ 85 | MkProgressBar }}
///

## With Full Context
/// mknodes | context
{{ "Full Context" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This block uses full context with all features", typ="warning") }}
{{ mk.MkCode(content="print('Full context available!')", language="python") }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    # Test with default config (no context)
    print("Testing with default config + per-block overrides:")
    md = markdown.Markdown(extensions=[makeMkNodesExtension()])
    result = md.convert(markdown_content)

    print("✅ Rendered successfully with mixed context settings")
    print(f"Result length: {len(result)} characters")
    print("\n" + "=" * 60 + "\n")


def programmatic_examples():
    """Show programmatic configuration examples."""
    print("=== Programmatic Configuration Examples ===")

    simple_content = """
/// mknodes
{{ "Programmatic Test" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="Testing programmatic configuration", typ="info") }}
///
"""

    from mknodes.mdext import makeMkNodesExtension

    print("1. Extension with default (no context, fast):")
    md1 = markdown.Markdown(extensions=[makeMkNodesExtension()])
    md1.convert(simple_content)
    print("✅ Configured with context=False (default)")

    print("\n2. Extension with explicit context=False:")
    md2 = markdown.Markdown(extensions=[makeMkNodesExtension(context=False)])
    md2.convert(simple_content)
    print("✅ Configured with context=False")

    print("\n3. Extension with context=True (full context):")
    md3 = markdown.Markdown(extensions=[makeMkNodesExtension(context=True)])
    md3.convert(simple_content)
    print("✅ Configured with context=True")

    print("\n4. Multiple extensions with MkNodes:")
    md4 = markdown.Markdown(
        extensions=[
            "admonition",
            "pymdownx.superfences",
            "tables",
            makeMkNodesExtension(),  # Default: no context
        ]
    )
    md4.convert(simple_content)
    print("✅ Configured with multiple extensions")

    print("\n" + "=" * 60 + "\n")


def performance_scenario_examples():
    """Show examples for different performance scenarios."""
    print("=== Performance Scenario Examples ===")

    scenarios = [
        {
            "name": "Development Environment (needs full context)",
            "config": "context: true",
            "reason": "Complete functionality needed during development",
            "yaml": """
markdown_extensions:
  - mknodes.mdext:
      context: true
""",
        },
        {
            "name": "Production Website",
            "config": "context: false (default)",
            "reason": "Fast rendering for better user experience",
            "yaml": """
markdown_extensions:
  - mknodes.mdext
""",
        },
        {
            "name": "CI/CD Documentation Build",
            "config": "context: false (default)",
            "reason": "Faster build times in automated pipelines",
            "yaml": """
markdown_extensions:
  - mknodes.mdext
""",
        },
        {
            "name": "Mixed Content Site",
            "config": "default + per-block context",
            "reason": "Default fast rendering with per-block full context when needed",
            "yaml": """
markdown_extensions:
  - mknodes.mdext
""",
            "markdown": """
# Mixed content example

## Fast content (default)
/// mknodes
{{ "Quick render" | MkHeader(level=3) }}
///

## Complex content (when full context needed)
/// mknodes | context
{{ "Rich content with full context" | MkHeader(level=3) }}
///
""",
        },
    ]

    for scenario in scenarios:
        print(f"**{scenario['name']}**")
        print(f"Context mode: {scenario['config']}")
        print(f"Reason: {scenario['reason']}")
        print("mkdocs.yml configuration:")
        print(scenario["yaml"])
        if "markdown" in scenario:
            print("Markdown example:")
            print(scenario["markdown"])
        print("-" * 40)


def real_world_examples():
    """Show real-world configuration examples."""
    print("=== Real-World Configuration Examples ===")

    examples = {
        "Personal Blog": {
            "description": "Simple blog with occasional dynamic content",
            "mkdocs_yml": """
site_name: My Personal Blog
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - mknodes.mdext  # Default: no context (fast)
""",
            "usage": "Most content is static, MkNodes used for simple dynamic elements",
        },
        "API Documentation": {
            "description": "Complex documentation with lots of generated content",
            "mkdocs_yml": """
site_name: API Documentation
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - pymdownx.tabbed
  - tables
  - mknodes.mdext:
      context: true  # Need all features
""",
            "usage": "Heavy use of MkNodes for API examples, tables, code blocks",
        },
        "Corporate Website": {
            "description": "High-traffic site needing fast performance",
            "mkdocs_yml": """
site_name: Corporate Website
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - mknodes.mdext  # Default: no context (fast)
""",
            "usage": "Performance is key, use per-block '| context' only when needed",
        },
        "Development Docs": {
            "description": "Internal documentation with rich content",
            "mkdocs_yml": """
site_name: Development Documentation
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - pymdownx.tabbed
  - pymdownx.highlight
  - tables
  - toc
  - mknodes.mdext:
      context: true  # All features available
""",
            "usage": "Internal use, full functionality more important than performance",
        },
    }

    for name, config in examples.items():
        print(f"**{name}**")
        print(f"Description: {config['description']}")
        print("Configuration:")
        print(config["mkdocs_yml"])
        print(f"Usage pattern: {config['usage']}")
        print("-" * 50)


def migration_examples():
    """Show how to migrate from old configurations."""
    print("=== Migration Examples ===")

    print("""
**Default behavior (no context, fast):**

mkdocs.yml:
```yaml
markdown_extensions:
  - mknodes.mdext
```

**With full context (when needed):**

```yaml
markdown_extensions:
  - mknodes.mdext:
      context: true
```

**Mixed approach (default fast, per-block context when needed):**

mkdocs.yml:
```yaml
markdown_extensions:
  - mknodes.mdext  # Default: context=false
```

Then use per-block context when needed:
```markdown
/// mknodes | context
{{ "Complex content needing full context" | MkHeader }}
///
```
""")


if __name__ == "__main__":
    print("MkNodes Extension Configuration Guide")
    print("=" * 50)

    try:
        mkdocs_yml_examples()
        per_block_examples()
        programmatic_examples()
        performance_scenario_examples()
        real_world_examples()
        migration_examples()

        print("✅ All configuration examples completed!")
        print("\nRecommendation:")
        print("- Default (context=false) is ~50x faster - use for most cases")
        print("- Use context=true only when you need full project info")
        print("- Use '/// mknodes | context' for per-block full context")

    except Exception as e:  # noqa: BLE001
        print(f"❌ Error in configuration examples: {e}")
        import traceback

        traceback.print_exc()

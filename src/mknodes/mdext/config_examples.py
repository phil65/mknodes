"""Configuration examples for MkNodes markdown extension.

This file demonstrates the different ways to configure the context mode
for the MkNodes extension, both globally via mkdocs.yml and per-block.
"""

from __future__ import annotations

import markdown


def mkdocs_yml_examples():
    """Show how to configure the extension in mkdocs.yml."""
    print("=== MkDocs YAML Configuration Examples ===")
    print("""
# mkdocs.yml - Global fallback context for better performance
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback

# mkdocs.yml - Full context for complete functionality (default)
markdown_extensions:
  - mknodes.mdext:
      context_mode: full

# mkdocs.yml - Combined with other extensions
markdown_extensions:
  - admonition
  - pymdownx.superfences
  - pymdownx.tabbed
  - tables
  - mknodes.mdext:
      context_mode: fallback  # Fast rendering for production
""")


def per_block_examples():
    """Demonstrate per-block context mode configuration."""
    print("=== Per-Block Configuration Examples ===")

    # Example markdown with different block modes
    markdown_content = """
# Per-Block Context Mode Demo

## Default Mode (uses global config)
/// mknodes
{{ "Default Context" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="Uses the globally configured context mode", typ="info") }}
///

## Explicit Fallback Mode
/// mknodes | fallback
{{ "Fast Rendering" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This block uses fallback context for speed", typ="success") }}
{{ 85 | MkProgressBar }}
///

## Explicit Full Mode
/// mknodes | full
{{ "Complete Context" | MkHeader(level=3) }}
{{ mk.MkAdmonition(content="This block uses full context with all features", typ="warning") }}
{{ mk.MkCode(content="print('Full context available!')", language="python") }}
///

## Alternative Syntax (aliases work)
/// mknodes | fast
{{ "Fast Alias" | MkHeader(level=3) }}
{{ mk.MkText("'fast', 'minimal' are aliases for 'fallback'") }}
///

/// mknodes | complete
{{ "Complete Alias" | MkHeader(level=3) }}
{{ mk.MkText("'complete', 'rich' are aliases for 'full'") }}
///
"""

    from mknodes.mdext import makeExtension

    # Test with global fallback config
    print("Testing with global fallback config + per-block overrides:")
    md = markdown.Markdown(extensions=[makeExtension(context_mode="fallback")])
    result = md.convert(markdown_content)

    print("✅ Rendered successfully with mixed context modes")
    print(f"Result length: {len(result)} characters")
    print("\n" + "=" * 60 + "\n")


def programmatic_examples():
    """Show programmatic configuration examples."""
    print("=== Programmatic Configuration Examples ===")

    simple_content = """
/// mknodes | fallback
{{ "Programmatic Test" | MkHeader(level=2) }}
{{ mk.MkAdmonition(content="Testing programmatic configuration", typ="info") }}
///
"""

    from mknodes.mdext import makeExtension

    print("1. Extension with global fallback context:")
    md1 = markdown.Markdown(extensions=[makeExtension(context_mode="fallback")])
    result1 = md1.convert(simple_content)
    print("✅ Configured for fallback context")

    print("\n2. Extension with global full context:")
    md2 = markdown.Markdown(extensions=[makeExtension(context_mode="full")])
    result2 = md2.convert(simple_content)
    print("✅ Configured for full context")

    print("\n3. Extension with default settings:")
    md3 = markdown.Markdown(extensions=[makeExtension()])
    result3 = md3.convert(simple_content)
    print("✅ Using default context mode")

    print("\n4. Multiple extensions with MkNodes:")
    md4 = markdown.Markdown(
        extensions=[
            "admonition",
            "pymdownx.superfences",
            "tables",
            makeExtension(context_mode="fallback"),
        ]
    )
    result4 = md4.convert(simple_content)
    print("✅ Configured with multiple extensions")

    print("\n" + "=" * 60 + "\n")


def performance_scenario_examples():
    """Show examples for different performance scenarios."""
    print("=== Performance Scenario Examples ===")

    scenarios = [
        {
            "name": "Development Environment",
            "config": "full",
            "reason": "Complete functionality needed during development",
            "yaml": """
markdown_extensions:
  - mknodes.mdext:
      context_mode: full
""",
        },
        {
            "name": "Production Website",
            "config": "fallback",
            "reason": "Fast rendering for better user experience",
            "yaml": """
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback
""",
        },
        {
            "name": "CI/CD Documentation Build",
            "config": "fallback",
            "reason": "Faster build times in automated pipelines",
            "yaml": """
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback
""",
        },
        {
            "name": "Mixed Content Site",
            "config": "fallback",
            "reason": "Global fallback with per-block full context when needed",
            "yaml": """
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback
""",
            "markdown": """
# Mixed content example

## Fast content
/// mknodes
{{ "Quick render" | MkHeader(level=3) }}
///

## Complex content (when full context needed)
/// mknodes | full
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
  - mknodes.mdext:
      context_mode: fallback  # Fast rendering
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
      context_mode: full  # Need all features
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
  - mknodes.mdext:
      context_mode: fallback  # Performance critical
""",
            "usage": "Performance is key, use per-block 'full' mode only when needed",
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
      context_mode: full  # All features available
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
**Before (no context mode configuration):**

mkdocs.yml:
```yaml
markdown_extensions:
  - mknodes.mdext
```

**After (explicit configuration):**

Option 1 - Keep existing behavior (full context):
```yaml
markdown_extensions:
  - mknodes.mdext:
      context_mode: full
```

Option 2 - Optimize for performance:
```yaml
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback
```

Option 3 - Mixed approach (fallback by default, full when needed):
```yaml
markdown_extensions:
  - mknodes.mdext:
      context_mode: fallback
```

Then use per-block full context when needed:
```markdown
/// mknodes | full
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
        print("- Use 'fallback' context mode for production/performance")
        print("- Use 'full' context mode for development/full features")
        print("- Use per-block overrides for fine-grained control")

    except Exception as e:
        print(f"❌ Error in configuration examples: {e}")
        import traceback

        traceback.print_exc()

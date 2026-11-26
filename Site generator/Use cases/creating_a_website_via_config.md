# Creating a website via config

It is possible to construct a basic documentation website without writing any Python code by
describing the node tree in the config. The default build function (`mknodes.site:parse`)
builds the nav from the `pages` setting.

The following config...

```toml
# pyproject.toml
[[tool.mknodes.pages]]
title = "Home"
type = "MkText"
text = "{{ metadata.description }}"
is_index = true

[[tool.mknodes.pages]]
Usage = [
  { title = "Getting started", type = "MkText", text = "Install the package and import it." },
  { title = "Changelog", type = "MkChangelog" },
]

[[tool.mknodes.pages]]
title = "API"
type = "MkDoc"
section_name = "API"
recursive = true

[[tool.mknodes.pages]]
title = "CLI"
type = "MkCliDoc"
show_subcommands = true
condition = "{{ metadata.cli }}"

[[tool.mknodes.pages]]
Development = [
  { title = "Contributing", type = "MkCommitConventions" },
  { title = "Dependencies", type = "MkDependencyTable" },
  { title = "License", type = "MkLicense" },
]

```

Combined with this CLI call...

```terminal
mknodes build
```

...creates a website with a home page, a usage section, API docs, a CLI page
(if the project has a CLI) and a development section.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.site.use_cases_section._**

```python
@nav.route.page("Creating a website via config", hide="toc")
def _(page: mk.MkPage):
    """Create the "Creating a website via config" MkPage."""
    config = (paths.RESOURCES / "pages_example.toml").read_text("utf-8")
    variables = {"config": config}
    page += mk.MkTemplate("site/use_case_default_website.jinja", variables=variables)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'pymdownx.highlight': {'anchor_linenums': True,
                                                      'line_spans': '__span',
                                                      'pygments_lang_class': True},
                               'pymdownx.superfences': {}},
          plugins=[],
          js=[],
          assets=[],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/use_cases_section.py
  source_function: _
  source_line_no: 13
hide:
- toc
title: Creating a website via config

```

</details>

</details>

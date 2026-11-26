# Core API

The classes you build a documentation with. Nodes (the Markdown fragments, from
[MkText](../The%20nodes/Base%20nodes/mktext.md#mknodes.MkText) to [MkDocStrings](../Get%20started/a_quick_node_tour.md#mknodes.MkDocStrings)) are documented on
their own pages in [The nodes](<../The nodes/index.md>), each with live examples. The
settings of the site generator (`[tool.mknodes]` / the `mknodes` plugin entry) are
listed on [Site generator / Configuration](<../Site generator/configuration.md>).

| Page                                | Objects                                                                                                                                                                                                                                                                                                  |
| ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| [Navs and pages](navs_and_pages.md) | [`MkNav`](navs_and_pages.md#mknodes.MkNav), [`MkPage`](navs_and_pages.md#mknodes.MkPage)                                                                                                                                                                                                                                                     |
| [Routing](routing.md)               | [`Router`](routing.md#mknodes.Router), [`NavRouter`](routing.md#mknodes.navs.navrouter.NavRouter)                                                                                                                                                                                                                              |
| [MkNode](mknode.md)                 | [`MkNode`](mknode.md#mknodes.MkNode)                                                                                                                                                                                                                                                                               |
| [Theming](theming.md)               | [`Theme`](theming.md#mknodes.Theme), [`MaterialTheme`](theming.md#mknodes.MaterialTheme)                                                                                                                                                                                                                                       |
| [Build step](build_step.md)         | [`DocBuilder`](build_step.md#mknodes.DocBuilder), [`BuildOutput`](build_step.md#mknodes.BuildOutput), [`NavItem`](build_step.md#mknodes.build.output.NavItem), [`MarkdownExporter`](build_step.md#mknodes.MarkdownExporter)                                                                                                                                      |
| [Rendering](rendering.md)           | [`get_renderer`](rendering.md#mknodes.rendering.get_renderer), [`use`](rendering.md#mknodes.rendering.use), [`Renderer`](rendering.md#mknodes.rendering.Renderer), [`MaterialRenderer`](rendering.md#mknodes.rendering.MaterialRenderer), [`GithubRenderer`](rendering.md#mknodes.rendering.github.GithubRenderer), [`MystRenderer`](rendering.md#mknodes.rendering.myst.MystRenderer) |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.api_section._**

```python
@nav.route.page(is_index=True, hide="toc", icon="api")
def _(page: mk.MkPage) -> None:
    page += INDEX_TEXT
    table = mk.MkTable(columns=["Page", "Objects"])
    for title, identifiers in PAGES.items():
        filename = f"{title.lower().replace(' ', '_')}.md"
        objects = ", ".join(f"[`{i.rsplit('.', 1)[-1]}`][{i}]" for i in identifiers)
        table.add_row((f"[{title}]({filename})", objects))
    page += table

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'tables': {}},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/api_section.py
  source_function: _
  source_line_no: 176
hide:
- toc
icon: material/api
title: Core API

```

</details>

</details>

# Documentation nodes

| Node                                                                                                                                                                                                  | Docstrings                                                                                                                                                                                                                         | Markdown extensions    |
| ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| [<img src="https://api.iconify.design/mdi/graph-outline.svg?height=16" alt="graph-outline"> MkClassDiagram](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkclassdiagram/)           | Node to display the class hierarchy of a class. Supports multiple modes.                                                                                                                                                           | `pymdownx.superfences` |
| [<img src="https://api.iconify.design/mdi/api.svg?height=16" alt="api"> MkDocStrings](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkdocstrings/)                                   | Docstring section (powered by mkdocstrings).                                                                                                                                                                                       |                        |
| [<img src="https://api.iconify.design/mdi/code-json.svg?height=16" alt="code-json"> MkCommentedCode](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkcommentedcode/)                 | Node which displays a list of code / comment blocks for given code.<br><br>Lines beginning with # are shown in dedicated blocks and can be used to<br>inline-explain the code. Lines can be hidden by ending a line with "##".<br> |                        |
| [<img src="https://api.iconify.design/mdi/library.svg?height=16" alt="library"> MkConfigSetting](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkconfigsetting/)                     | Node for describing a config setting.                                                                                                                                                                                              |                        |
| [<img src="https://api.iconify.design/mdi/database.svg?height=16" alt="database"> MkClassTable](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkclasstable/)                         | Node for a table showing info for a list of classes.                                                                                                                                                                               | `tables`               |
| [<img src="https://api.iconify.design/mdi/view-module-outline.svg?height=16" alt="view-module-outline"> MkModuleTable](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkmoduletable/) | Node for a table containing formatted information about a module.                                                                                                                                                                  | `tables`               |
| [<img src="https://api.iconify.design/mdi/api.svg?height=16" alt="api"> MkCliDoc](https://phil65.github.io/mknodes/The nodes/Documentation nodes/mkclidoc/)                                           | Node for showing documentation for click / typer CLI apps.                                                                                                                                                                         |                        |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("Documentation nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, DOCUMENTATION_NODES)
    page.created_by = create_section_for_nodes

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/nodes_section.py
  source_function: _
  source_line_no: 165
hide:
- toc
title: Documentation nodes

```

</details>

</details>

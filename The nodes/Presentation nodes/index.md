# Presentation nodes

| Node                                                                                                                                                                                           | Docstrings                                                                                                                                                                                                                                                                                                                                                                               | Markdown extensions                          |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------- |
| [<img src="https://api.iconify.design/mdi/file-tree-outline.svg?height=16" alt="file-tree-outline"> MkTreeView](https://phil65.github.io/mknodes/The nodes/Presentation nodes/mktreeview/)     | Node to display tree structures.<br><br>Currently supports directories and Node subclasses (including `MkNodes`).<br>                                                                                                                                                                                                                                                                    | `pymdownx.highlight`, `pymdownx.superfences` |
| [<img src="https://api.iconify.design/mdi/presentation.svg?height=16" alt="presentation"> MkReprRawRendered](https://phil65.github.io/mknodes/The nodes/Presentation nodes/mkreprrawrendered/) | Node showing a tabbed block to visualize a node in different representations.<br><br>It contains a tab for the repr, one for the rendered output,<br>one for the markdown and a Repr tree in case the node has children.<br>The node can also be a string with a jinja macro returning an MkNode.<br>In that case a "Jinja" tab containing the macro is prepended to the other tabs.<br> |                                              |
| [<img src="https://api.iconify.design/mdi/graph-outline.svg?height=16" alt="graph-outline"> MkDiagram](https://phil65.github.io/mknodes/The nodes/Presentation nodes/mkdiagram/)               | Class representing a mermaid diagram.<br><br>MkDiagrams can show directed acyclic graphs and allows to manually<br>create diagrams.<br>                                                                                                                                                                                                                                                  | `pymdownx.superfences`                       |
| [<img src="https://api.iconify.design/mdi/timeline.svg?height=16" alt="timeline"> MkTimeline](https://phil65.github.io/mknodes/The nodes/Presentation nodes/mktimeline/)                       | Node to show a JavaScript-supported Timeline.<br><br>Consists of cards which slide in and out once they enter / leave the screen.<br>                                                                                                                                                                                                                                                    |                                              |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("Presentation nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, PRESENTATION_NODES)
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
  source_line_no: 158
hide:
- toc
title: Presentation nodes

```

</details>

</details>

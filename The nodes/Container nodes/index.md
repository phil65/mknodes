# Container nodes

| Node                                                                                                                                                                                        | Docstrings                                                                                                                                                                                                                                       | Markdown extensions                                      |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------- |
| [<img src="https://api.iconify.design/mdi/format-quote-open.svg?height=16" alt="format-quote-open"> MkBlockQuote](https://phil65.github.io/mknodes/The nodes/Container nodes/mkblockquote/) | BlockQuote node.                                                                                                                                                                                                                                 |                                                          |
| [<img src="https://api.iconify.design/octicon/info-16.svg?height=16" alt="info-16"> MkAdmonition](https://phil65.github.io/mknodes/The nodes/Container nodes/mkadmonition/)                 | Admonition info box.                                                                                                                                                                                                                             | `admonition`, `pymdownx.details`, `pymdownx.superfences` |
| [<img src="https://api.iconify.design/mdi/database.svg?height=16" alt="database"> MkContainer](https://phil65.github.io/mknodes/The nodes/Container nodes/mkcontainer/)                     | A node containing other MkNodes.<br><br>This is the concrete implementation with list-based storage.<br>Can be used directly or as a base class.<br>Nodes added to a container are automatically re-parented.<br>                                |                                                          |
| [<img src="https://api.iconify.design/mdi/code-json.svg?height=16" alt="code-json"> MkCode](https://phil65.github.io/mknodes/The nodes/Container nodes/mkcode/)                             | Class representing a Code block.                                                                                                                                                                                                                 | `pymdownx.highlight`, `pymdownx.superfences`             |
| [<img src="https://api.iconify.design/octicon/list-unordered-24.svg?height=16" alt="list-unordered-24"> MkList](https://phil65.github.io/mknodes/The nodes/Container nodes/mklist/)         | Node for showing a formatted list.                                                                                                                                                                                                               | `def_list`                                               |
| [<img src="https://api.iconify.design/octicon/table-24.svg?height=16" alt="table-24"> MkTable](https://phil65.github.io/mknodes/The nodes/Container nodes/mktable/)                         | Class representing a formatted table.<br><br>Data: a mapping column -> cells, a list of rows (the first one is the header unless<br>`columns` are given) or a list of dicts (see `MkBaseTable`). `\|` in cells gets escaped.<br>                 | `tables`                                                 |
| [<img src="https://api.iconify.design/octicon/table-24.svg?height=16" alt="table-24"> MkHtmlTable](https://phil65.github.io/mknodes/The nodes/Container nodes/mkhtmltable/)                 | Class representing a html table.<br><br>Compared to MkTable, this will end up with a more verbose output,<br>but it can contain more complex Markdown in cells.<br>                                                                              |                                                          |
| [<img src="https://api.iconify.design/mdi/library.svg?height=16" alt="library"> MkDefinitionList](https://phil65.github.io/mknodes/The nodes/Container nodes/mkdefinitionlist/)             | Node for definition lists.                                                                                                                                                                                                                       | `def_list`                                               |
| [<img src="https://api.iconify.design/octicon/info-16.svg?height=16" alt="info-16"> MkDetailsBlock](https://phil65.github.io/mknodes/The nodes/Container nodes/mkdetailsblock/)             | Pymdownx-based details box.                                                                                                                                                                                                                      | `pymdownx.blocks.details`                                |
| [<img src="https://api.iconify.design/octicon/code-16.svg?height=16" alt="code-16"> MkHtmlBlock](https://phil65.github.io/mknodes/The nodes/Container nodes/mkhtmlblock/)                   | PyMdown-based Html block. Can be used to show raw content.                                                                                                                                                                                       | `pymdownx.blocks.html`                                   |
| [<img src="https://api.iconify.design/mdi/tab.svg?height=16" alt="tab"> MkTabbedBlocks](https://phil65.github.io/mknodes/The nodes/Container nodes/mktabbedblocks/)                         | PyMdown Block Extension Tab.                                                                                                                                                                                                                     | `pymdownx.blocks.tab`                                    |
| [<img src="https://api.iconify.design/mdi/tab.svg?height=16" alt="tab"> MkTabbed](https://phil65.github.io/mknodes/The nodes/Container nodes/mktabbed/)                                     | PyMdown-based Tab container.                                                                                                                                                                                                                     | `pymdownx.tabbed`, `pymdownx.superfences`                |
| [<img src="https://api.iconify.design/mdi/alert-box.svg?height=16" alt="alert-box"> MkAnnotations](https://phil65.github.io/mknodes/The nodes/Container nodes/mkannotations/)               | Node containing a list of MkAnnotations.                                                                                                                                                                                                         | `pymdownx.superfences`                                   |
| [<img src="https://api.iconify.design/octicon/list-ordered-16.svg?height=16" alt="list-ordered-16"> MkFootNotes](https://phil65.github.io/mknodes/The nodes/Container nodes/mkfootnotes/)   | Node containing a list of MkFootNotes.                                                                                                                                                                                                           | `footnotes`                                              |
| [<img src="https://api.iconify.design/mdi/view-grid.svg?height=16" alt="view-grid"> MkShowcase](https://phil65.github.io/mknodes/The nodes/Container nodes/mkshowcase/)                     | Node for showing a html-based image grid.<br><br>Manages row / column positioning.<br>Mainly intended for MkCards, but can also include other markdown (there are limits<br>though.)<br>When adding MkCards, then addtional CSS is required.<br> |                                                          |
| [<img src="https://api.iconify.design/mdi/library.svg?height=16" alt="library"> MkTaskList](https://phil65.github.io/mknodes/The nodes/Container nodes/mktasklist/)                         | Node for task lists.                                                                                                                                                                                                                             | `pymdownx.tasklist`                                      |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("Container nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, CONTAINER_NODES)
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
  source_line_no: 151
hide:
- toc
title: Container nodes

```

</details>

</details>

# Special nodes

| Node                                                                                                                                                                                          | Docstrings                                                                                                                                                                                                                                                                                             | Markdown extensions |
| --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| [<img src="https://api.iconify.design/octicon/file-symlink-file-24.svg?height=16" alt="file-symlink-file-24"> MkInclude](https://phil65.github.io/mknodes/The nodes/Special nodes/mkinclude/) | Node to include the text of other Markdown files / MkNodes.<br><br>This node only keeps a reference to given target and resolves it when needed.<br>Target can either be an URL or any other fsspec protocol path to a markdown file,<br>a file system path to a markdown file, or another MkNode.<br> |                     |
| [<img src="https://api.iconify.design/mdi/web-box.svg?height=16" alt="web-box"> MkIFrame](https://phil65.github.io/mknodes/The nodes/Special nodes/mkiframe/)                                 | Node for embedding an IFrame.                                                                                                                                                                                                                                                                          |                     |
| [<img src="https://api.iconify.design/mdi/bash.svg?height=16" alt="bash"> MkCommandOutput](https://phil65.github.io/mknodes/The nodes/Special nodes/mkcommandoutput/)                         | Node to display the terminal output of a command.                                                                                                                                                                                                                                                      |                     |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("Special nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, SPECIAL_NODES)
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
  source_line_no: 179
hide:
- toc
title: Special nodes

```

</details>

</details>

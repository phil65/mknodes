# Base nodes

| Node                                                                                                                                                                                   | Docstrings                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        | Markdown extensions    |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------- |
| [<img src="https://api.iconify.design/mdi/puzzle-outline.svg?height=16" alt="puzzle-outline"> MkNode](https://phil65.github.io/mknodes/The nodes/Base nodes/mknode/)                   | Base class for everything which can be expressed as Markup.<br><br>This class combines tree node functionality with markdown generation.<br>Starting from the root nav (aka Docs) down to nested Markup blocks,<br>the whole project can be represented by one tree.<br><br>MkNode is the base class for all nodes. We dont instanciate it directly.<br>All subclasses carry an MkAnnotations node (except the MkAnnotations node itself)<br>They can also pass an `indent` as well as a `shift_header_levels` keyword argument<br>in order to modify the resulting markdown.<br> |                        |
| [<img src="https://api.iconify.design/mdi/text.svg?height=16" alt="text"> MkText](https://phil65.github.io/mknodes/The nodes/Base nodes/mktext/)                                       | Class for any Markup text.<br><br>All classes inheriting from MkNode can get converted to this Type.<br>                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |                        |
| [<img src="https://api.iconify.design/mdi/format-header-pound.svg?height=16" alt="format-header-pound"> MkHeader](https://phil65.github.io/mknodes/The nodes/Base nodes/mkheader/)     | Super simple header node.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |                        |
| [<img src="https://api.iconify.design/octicon/info-16.svg?height=16" alt="info-16"> MkCompactAdmonition](https://phil65.github.io/mknodes/The nodes/Base nodes/mkcompactadmonition/)   | Compact admonition info box.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      |                        |
| [<img src="https://api.iconify.design/mdi/format-text.svg?height=16" alt="format-text"> MkCritic](https://phil65.github.io/mknodes/The nodes/Base nodes/mkcritic/)                     | MkCritic block.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   | `pymdownx.critic`      |
| [<img src="https://api.iconify.design/octicon/link-24.svg?height=16" alt="link-24"> MkLink](https://phil65.github.io/mknodes/The nodes/Base nodes/mklink/)                             | A simple Link (with optional icon and option to show up as a button).<br><br>If no title is given, the URL is used as a title.<br>                                                                                                                                                                                                                                                                                                                                                                                                                                                |                        |
| [<img src="https://api.iconify.design/fa6-regular/keyboard.svg?height=16" alt="keyboard"> MkKeys](https://phil65.github.io/mknodes/The nodes/Base nodes/mkkeys/)                       | Node to display Keyboard keys.<br><br>Mostly used to explain shortcuts / commands for the keyboard.<br>                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | `pymdownx.keys`        |
| [<img src="https://api.iconify.design/fa6-solid/bars-progress.svg?height=16" alt="bars-progress"> MkProgressBar](https://phil65.github.io/mknodes/The nodes/Base nodes/mkprogressbar/) | Node to display a CSS-based progress bar.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         | `pymdownx.progressbar` |
| [<img src="https://api.iconify.design/mdi/chat.svg?height=16" alt="chat"> MkSpeechBubble](https://phil65.github.io/mknodes/The nodes/Base nodes/mkspeechbubble/)                       | Node for showing a css-based speech bubble.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       |                        |
| [<img src="https://api.iconify.design/simple-icons/jinja.svg?height=16" alt="jinja"> MkTemplate](https://phil65.github.io/mknodes/The nodes/Base nodes/mktemplate/)                    | Node representing a jinja template.<br><br>Renders templates with the context-aware MkNodes jinja environment.<br>Rendered nodes become virtual children of this node.<br>Additional variables can be passed to the render process.<br>                                                                                                                                                                                                                                                                                                                                           |                        |
| [<img src="https://api.iconify.design/mdi/format-list-group.svg?height=16" alt="format-list-group"> MkLlm](https://phil65.github.io/mknodes/The nodes/Base nodes/mkllm/)               | Node for LLM-based text generation.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |                        |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("Base nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, BASE_NODES)
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
  source_line_no: 137
hide:
- toc
title: Base nodes

```

</details>

</details>

# Image nodes

| Node                                                                                                                                                                                         | Docstrings                                                                                                                                                                                                                                                   | Markdown extensions |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | ------------------- |
| [<img src="https://api.iconify.design/mdi/image.svg?height=16" alt="image"> MkImage](https://phil65.github.io/mknodes/The nodes/Image nodes/mkimage/)                                        | Image including optional caption.                                                                                                                                                                                                                            |                     |
| [<img src="https://api.iconify.design/mdi/image-off.svg?height=16" alt="image-off"> MkImageCompare](https://phil65.github.io/mknodes/The nodes/Image nodes/mkimagecompare/)                  | Node to show an Image comparison (using a slider).                                                                                                                                                                                                           |                     |
| [<img src="https://api.iconify.design/mdi/image-multiple.svg?height=16" alt="image-multiple"> MkImageSlideshow](https://phil65.github.io/mknodes/The nodes/Image nodes/mkimageslideshow/)    | Node to show an Image slideshow (in autoplay mode).                                                                                                                                                                                                          |                     |
| [<img src="https://api.iconify.design/simple-icons/shieldsdotio.svg?height=16" alt="shieldsdotio"> MkBadge](https://phil65.github.io/mknodes/The nodes/Image nodes/mkbadge/)                 | Node for a locally-created badge (based on "anybadge").<br><br>The node creates a badge svg, appends it to the virtual files, and<br>shows it as an image.<br>                                                                                               |                     |
| [<img src="https://api.iconify.design/mdi/image.svg?height=16" alt="image"> MkIcon](https://phil65.github.io/mknodes/The nodes/Image nodes/mkicon/)                                          | Pyconify-based Icon.                                                                                                                                                                                                                                         |                     |
| [<img src="https://api.iconify.design/simple-icons/shieldsdotio.svg?height=16" alt="shieldsdotio"> MkMaterialBadge](https://phil65.github.io/mknodes/The nodes/Image nodes/mkmaterialbadge/) | Node for a CSS-based badge a la MkDocs-Material.                                                                                                                                                                                                             |                     |
| [<img src="https://api.iconify.design/mdi/file-image.svg?height=16" alt="file-image"> MkBinaryImage](https://phil65.github.io/mknodes/The nodes/Image nodes/mkbinaryimage/)                  | Image carrying the data by itself.<br><br>This node basically is a regular image link, but carries the image data by itself.<br>The data will get written to the "virtual" folder at the end of the process.<br>It can hold either str or bytes as data.<br> |                     |
| [<img src="https://api.iconify.design/mdi/square-medium.svg?height=16" alt="square-medium"> MkCard](https://phil65.github.io/mknodes/The nodes/Image nodes/mkcard/)                          | A card node, displaying an image, a button-like label and a hover caption.<br><br>This node requires addtional CSS to work.<br>                                                                                                                              |                     |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.nodes_section._**

```python
@nav.route.nav("Image nodes")
def _(nav: mk.MkNav) -> None:
    page = nav.add_page(is_index=True, hide="toc")
    page += create_section_for_nodes(nav, IMAGE_NODES)
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
  source_line_no: 144
hide:
- toc
title: Image nodes

```

</details>

</details>

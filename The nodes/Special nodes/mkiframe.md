# MkIFrame

[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github"> Show source on GitHub](https://github.com/phil65/mknodes/blob/main/src/mknodes/basenodes/mkiframe/__init__.py)

### Node for embedding an IFrame.

<details open>
<summary>Examples</summary>

### Example: **With caption**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "https://phil65.github.io/mknodes/" | MkIFrame(width=600, height=800) }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkIFrame('https://phil65.github.io/mknodes/', width=600, height=800)
> ```

<details open>
<summary>Rendered</summary>

<iframe width="600" height="800" src="https://phil65.github.io/mknodes/"></iframe>

</details>

<details>
<summary>Markdown</summary>

```markdown
<iframe width="600" height="800" src="https://phil65.github.io/mknodes/"></iframe>
```

</details>

<details>
<summary>Html</summary>

```html
<iframe width="600" height="800" src="https://phil65.github.io/mknodes/"></iframe>

```

</details>

</details>

<details open>
<summary>DocStrings</summary>

<a id="mknodes.MkIFrame"></a>

```python
class MkIFrame(mktemplate.MkTemplate)
```

</details>

<details open>
<summary>Base classes</summary>

| Name | Children | Inherits |
|--- | --- | --- |
| **<font size='4'>[MkTemplate](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.templatenodes.mktemplate</font>*<br>Node representing a jinja template\. | <ul><li>[MkCliDoc](https://phil65.github.io/mknodes/)</li><li>[MkMaterialBadge](https://phil65.github.io/mknodes/)</li><li>[MkImageCompare](https://phil65.github.io/mknodes/)</li><li>[MkImageSlideshow](https://phil65.github.io/mknodes/)</li><li>[MkIFrame](https://phil65.github.io/mknodes/)</li><li>[MkCard](https://phil65.github.io/mknodes/)</li><li>[MkInstallGuide](https://phil65.github.io/mknodes/)</li><li>[MkCodeOfConduct](https://phil65.github.io/mknodes/)</li><li>[MkCommitConventions](https://phil65.github.io/mknodes/)</li><li>[MkDevEnvSetup](https://phil65.github.io/mknodes/)</li><li>[MkDevTools](https://phil65.github.io/mknodes/)</li><li>...</li></ul> | <ul><li>[TemplateRenderMixin](https://phil65.github.io/mknodes/)</li><li>[MkContainer](https://phil65.github.io/mknodes/)</li></ul> |

</details>

<details>
<summary>⋔ Inheritance diagram</summary>

```mermaid
graph TD
  3066175229["mkiframe.MkIFrame"]
  1289759389["mktemplate.MkTemplate"]
  3160803176["rendercache.TemplateRenderMixin"]
  2751680898["builtins.object"]
  835538629["mkcontainer.MkContainer"]
  1956333208["mkcontainer.MkContainerBase"]
  1359323199["mknode.MkNode"]
  1289759389 --> 3066175229
  3160803176 --> 1289759389
  2751680898 --> 3160803176
  835538629 --> 1289759389
  1956333208 --> 835538629
  1359323199 --> 1956333208
  2751680898 --> 1359323199
```

</details>

<details>
<summary>NodeFile</summary>

**/home/runner/work/mknodes/mknodes/src/mknodes/basenodes/mkiframe/metadata.toml**

```toml
[metadata]
icon = "mdi:web-box"
name = "MkIFrame"

[examples.with_caption]
title = "With caption"
jinja = """
{{ "https://phil65.github.io/mknodes/" | MkIFrame(width=600, height=800) }}
"""

[output.html]
template = """
<iframe width="{{ node.width }}" height="{{ node.height }}" src="{{ node.url }}"></iframe>
"""

```

</details>

<details>
<summary>Code</summary>

**mknodes.basenodes.mkiframe.MkIFrame**

```python
class MkIFrame(mktemplate.MkTemplate):
    """Node for embedding an IFrame."""

    ICON = "material/web-box"

    def __init__(
        self,
        url: str,
        *,
        width: int = 300,
        height: int = 150,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            url: Url to display in a frame
            width: width of frame in pixels
            height: height of frame in pixels
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/html/template", **kwargs)
        self.url = url
        self.width = width
        self.height = height

```

</details>

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.nodes_section.create_section_for_nodes**

```python
def create_section_for_nodes(
    nav: mk.MkNav,
    klasses: Sequence[type[mk.MkNode]],
) -> mk.MkTable:
    table = mk.MkTable(columns=["Node", "Docstrings", "Markdown extensions"])
    for kls in klasses:
        tpl = "classpage_custom.jinja"
        page = mk.MkClassPage(kls, icon=kls.ICON, template_path=tpl, parent=nav, hide="toc")
        nav += page
        if kls.STATUS:
            page.metadata.status = kls.STATUS
        elif kls.JS_FILES:
            page.metadata.status = "js"
        elif kls.CSS:
            page.metadata.status = "css"
        page.created_by = create_section_for_nodes
        link = mk.MkLink(page, kls.__name__, icon=kls.ICON)
        extensions = ", ".join(f"`{i}`" for i in kls.REQUIRED_EXTENSIONS)
        table.add_row((link, kls.__doc__, extensions))
    return table

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'admonition': {},
                               'pymdownx.details': {},
                               'pymdownx.highlight': {'anchor_linenums': True,
                                                      'line_spans': '__span',
                                                      'pygments_lang_class': True},
                               'pymdownx.superfences': {'custom_fences': [{'class': 'mermaid',
                                                                           'format': <function fence_code_format at 0x7bb797a5c1a0>,
                                                                           'name': 'mermaid'}]},
                               'pymdownx.tabbed': {},
                               'tables': {}},
          plugins=[Plugin('mkdocstrings')],
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
  source_function: create_section_for_nodes
  source_line_no: 93
hide:
- toc
icon: material/web-box
status: new
title: MkIFrame

```

</details>

</details>

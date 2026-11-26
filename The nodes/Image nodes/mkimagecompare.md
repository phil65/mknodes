# MkImageCompare

[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github"> Show source on GitHub](https://github.com/phil65/mknodes/blob/main/src/mknodes/basenodes/mkimagecompare/__init__.py)

### Node to show an Image comparison (using a slider).

<details open>
<summary>Examples</summary>

### Example: **Regular**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "https://picsum.photos/700" | MkImageCompare(after_image="https://picsum.photos/701") }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkImageCompare('https://picsum.photos/700', 'https://picsum.photos/701')
> ```

<details open>
<summary>Rendered</summary>

<img-comparison-slider>
  <img src="https://picsum.photos/700" slot="first">
  <img src="https://picsum.photos/701" slot="second">
</img-comparison-slider>

</details>

<details>
<summary>Markdown</summary>

```markdown
<img-comparison-slider>
  <img src="https://picsum.photos/700" slot="first">
  <img src="https://picsum.photos/701" slot="second">
</img-comparison-slider>
```

</details>

<details>
<summary>Html</summary>

```html
<img-comparison-slider>
  <img src="https://picsum.photos/700" slot="first">
  <img src="https://picsum.photos/701" slot="second">
</img-comparison-slider>

```

</details>

</details>

<details open>
<summary>DocStrings</summary>

<a id="mknodes.MkImageCompare"></a>

```python
class MkImageCompare(mktemplate.MkTemplate)
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
  800882708["mkimagecompare.MkImageCompare"]
  1289759389["mktemplate.MkTemplate"]
  3160803176["rendercache.TemplateRenderMixin"]
  2751680898["builtins.object"]
  835538629["mkcontainer.MkContainer"]
  1956333208["mkcontainer.MkContainerBase"]
  1359323199["mknode.MkNode"]
  1289759389 --> 800882708
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

**/home/runner/work/mknodes/mknodes/src/mknodes/basenodes/mkimagecompare/metadata.toml**

```toml
[metadata]
icon = "mdi:image-off"
name = "MkImageCompare"
group = "image"

[[resources.js]]
link = "https://unpkg.com/img-comparison-slider@7/dist/index.js"
defer = true

[[resources.css]]
filename = "https://unpkg.com/img-comparison-slider@7/dist/styles.css"


[examples.regular]
title = "Regular"
jinja = """
{{ "https://picsum.photos/700" | MkImageCompare(after_image="https://picsum.photos/701") }}
"""

[output.html]
template = """
<img-comparison-slider>
  <img src="{{ node.before_image }}" slot="first">
  <img src="{{ node.after_image }}" slot="second">
</img-comparison-slider>
"""

```

</details>

<details>
<summary>Code</summary>

**mknodes.basenodes.mkimagecompare.MkImageCompare**

```python
class MkImageCompare(mktemplate.MkTemplate):
    """Node to show an Image comparison (using a slider)."""

    ICON = "material/image-off"
    JS_FILES = [resources.JSFile(JS_URL, defer=True)]
    CSS = [resources.CSSFile(CSS_URL)]

    def __init__(
        self,
        before_image: str,
        after_image: str,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            before_image: Image shown with slider to the right
            after_image: Image shown with slider to the left
            kwargs: Keyword arguments passed to parent
        """
        super().__init__("output/html/template", **kwargs)
        self.before_image = before_image
        self.after_image = after_image

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
icon: material/image-off
status: new
title: MkImageCompare

```

</details>

</details>

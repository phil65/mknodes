# MkSpeechBubble

[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github"> Show source on GitHub](https://github.com/phil65/mknodes/blob/main/src/mknodes/basenodes/mkspeechbubble/__init__.py)

### Node for showing a css-based speech bubble.

<details open>
<summary>Examples</summary>

### Example: **Regular**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "some text" | MkSpeechBubble }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkSpeechBubble()
> ```

<details open>
<summary>Rendered</summary>

<div class="speech bottom">

some text

</div>

</details>

<details>
<summary>Markdown</summary>

```markdown
<div class="speech bottom">

some text

</div>
```

</details>

<details>
<summary>Html</summary>

```html
<div class="speech bottom">
<p>some text</p>
</div>

```

</details>

<details>
<summary>GitHub</summary>

```markdown
<div class="speech bottom">

some text

</div>
```

</details>

<details>
<summary>Repr tree</summary>

```
MkSpeechBubble
╰── MkText('some text')
```

</details>

### Example: **No arrow**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "some text" | MkSpeechBubble(arrow=None) }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkSpeechBubble(arrow=None)
> ```

<details open>
<summary>Rendered</summary>

<div class="speech">

some text

</div>

</details>

<details>
<summary>Markdown</summary>

```markdown
<div class="speech">

some text

</div>
```

</details>

<details>
<summary>Html</summary>

```html
<div class="speech">
<p>some text</p>
</div>

```

</details>

<details>
<summary>GitHub</summary>

```markdown
<div class="speech">

some text

</div>
```

</details>

<details>
<summary>Repr tree</summary>

```
MkSpeechBubble
╰── MkText('some text')
```

</details>

</details>

<details open>
<summary>DocStrings</summary>

<a id="mknodes.MkSpeechBubble"></a>

```python
class MkSpeechBubble(mkcontainer.MkContainer)
```

</details>

<details open>
<summary>Base classes</summary>

| Name | Children | Inherits |
|--- | --- | --- |
| **<font size='4'>[MkContainer](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkcontainer</font>*<br>A node containing other MkNodes\. | <ul><li>[MkBlock](https://phil65.github.io/mknodes/)</li><li>[MkAdmonition](https://phil65.github.io/mknodes/)</li><li>[MkBlockQuote](https://phil65.github.io/mknodes/)</li><li>[MkCode](https://phil65.github.io/mknodes/)</li><li>[MkTemplate](https://phil65.github.io/mknodes/)</li><li>[MkList](https://phil65.github.io/mknodes/)</li><li>[MkBaseTable](https://phil65.github.io/mknodes/)</li><li>[MkTab](https://phil65.github.io/mknodes/)</li><li>[MkTabContainer](https://phil65.github.io/mknodes/)</li><li>[MkCritic](https://phil65.github.io/mknodes/)</li><li>[MkAnnotation](https://phil65.github.io/mknodes/)</li><li>...</li></ul> | <ul><li>[MkContainerBase](https://phil65.github.io/mknodes/)</li></ul> |

</details>

<details>
<summary>⋔ Inheritance diagram</summary>

```mermaid
graph TD
  1965962441["mkspeechbubble.MkSpeechBubble"]
  835538629["mkcontainer.MkContainer"]
  1956333208["mkcontainer.MkContainerBase"]
  1359323199["mknode.MkNode"]
  2751680898["builtins.object"]
  835538629 --> 1965962441
  1956333208 --> 835538629
  1359323199 --> 1956333208
  2751680898 --> 1359323199
```

</details>

<details>
<summary>NodeFile</summary>

**/home/runner/work/mknodes/mknodes/src/mknodes/basenodes/mkspeechbubble/metadata.toml**

```toml
[metadata]
icon = "mdi:chat"
name = "MkSpeechBubble"

[[resources.css]]
filename = "speechbubble.css"

[examples.regular]
title = "Regular"
jinja = """
{{ "some text" | MkSpeechBubble }}
"""

[examples.no_arrow]
title = "No arrow"
jinja = """
{{ "some text" | MkSpeechBubble(arrow=None) }}
"""

[output.markdown]
template = """
<div class="speech{{ node.arrow | add(prefix=' ') }}" markdown="1">
{{node.get_items()  | join(node.block_separator) }}
</div>
"""

```

</details>

<details>
<summary>Code</summary>

**mknodes.basenodes.mkspeechbubble.MkSpeechBubble**

```python
class MkSpeechBubble(mkcontainer.MkContainer):
    """Node for showing a css-based speech bubble."""

    ICON = "material/chat"
    CSS = [resources.CSSFile("speechbubble.css")]

    def __init__(
        self,
        content: str | mknode.MkNode | list | None = None,
        *,
        arrow: Literal["top", "bottom", "left", "right"] | None = "bottom",
        **kwargs: Any,
    ) -> None:
        self.arrow = arrow
        super().__init__(content=content or [], **kwargs)

    def get_element(self) -> xml.Div:
        klass = f"speech {self.arrow}" if self.arrow else "speech"
        root = xml.Div(klass, markdown=True)
        root.text = "\n" + super().to_md_unprocessed() + "\n"
        return root

    def to_md_unprocessed(self) -> str:
        element = self.get_element()
        return element.to_string()

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
icon: material/chat
status: css
title: MkSpeechBubble

```

</details>

</details>

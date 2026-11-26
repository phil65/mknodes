# MkBlockQuote

[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github"> Show source on GitHub](https://github.com/phil65/mknodes/blob/main/src/mknodes/basenodes/mkblockquote/__init__.py)

### BlockQuote node.

<details open>
<summary>Examples</summary>

### Example: **Regular**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "Some text" | MkBlockQuote }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkBlockQuote()
> ```

<details open>
<summary>Rendered</summary>

> Some text

</details>

<details>
<summary>Markdown</summary>

```markdown
> Some text

```

</details>

<details>
<summary>Html</summary>

```html
<blockquote>
<p>Some text</p>
</blockquote>

```

</details>

<details>
<summary>reST</summary>

```rst
    Some text

```

</details>

<details>
<summary>Repr tree</summary>

```
MkBlockQuote
╰── MkText('Some text')
```

</details>

### Example: **Nested**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "Nested!" | MkBlockQuote | MkBlockQuote }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkContainer()
> ```

<details open>
<summary>Rendered</summary>

> Nested!

> > Nested!

</details>

<details>
<summary>Markdown</summary>

```markdown
> Nested!

> > Nested!

```

</details>

<details>
<summary>Html</summary>

```html
<blockquote>
<p>Nested!</p>
</blockquote>
<blockquote>
<blockquote>
<p>Nested!</p>
</blockquote>
</blockquote>

```

</details>

<details>
<summary>Repr tree</summary>

```
MkContainer
├── MkBlockQuote()
│   ╰── MkText('Nested!')
╰── MkBlockQuote()
├── MkBlockQuote()
│   ╰── MkText('Nested!')
```

</details>

</details>

<details open>
<summary>DocStrings</summary>

<a id="mknodes.MkBlockQuote"></a>

```python
class MkBlockQuote(mkcontainer.MkContainer)
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
  1647548858["mkblockquote.MkBlockQuote"]
  835538629["mkcontainer.MkContainer"]
  1956333208["mkcontainer.MkContainerBase"]
  1359323199["mknode.MkNode"]
  2751680898["builtins.object"]
  835538629 --> 1647548858
  1956333208 --> 835538629
  1359323199 --> 1956333208
  2751680898 --> 1359323199
```

</details>

<details>
<summary>NodeFile</summary>

**/home/runner/work/mknodes/mknodes/src/mknodes/basenodes/mkblockquote/metadata.toml**

```toml
[metadata]
icon = "mdi:format-quote-open"
name = "MkBlockQuote"

[examples.regular]
title = "Regular"
jinja = """
{{ "Some text" | MkBlockQuote }}
"""

[examples.nested]
title = "Nested"
description = "We can also nest blocks, they will adjust their delimiters automatically."
jinja = """
{{ "Nested!" | MkBlockQuote | MkBlockQuote }}
"""

[output.markdown]
template = """
{{ node.get_items() | join(node.block_separator) | indent(width="> ", first=True) | rstrip("\n") }}

"""

# [output.html]
# template = """
# <blockquote>
# {{ node.get_items() | join(node.block_separator)  }}
# </blockquote>
# """

[output.rst]
template = """
{{ node.get_items() | join(node.block_separator) | indent(width="    ", first=True) | rstrip("\n") }}

"""

```

</details>

<details>
<summary>Code</summary>

**mknodes.basenodes.mkblockquote.MkBlockQuote**

```python
class MkBlockQuote(mkcontainer.MkContainer):
    """BlockQuote node."""

    ICON = "material/format-quote-open"
    STATUS = "new"

    def get_content(self) -> resources.NodeContent:
        """Single-pass: get content and apply blockquote indentation."""
        content = super().get_content()
        md = textwrap.indent(content.markdown, "> ").rstrip("\n") + "\n"
        return resources.NodeContent(markdown=md, resources=content.resources)

    def to_md_unprocessed(self) -> str:
        content = self.get_content()
        return content.markdown

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
icon: material/format-quote-open
status: new
title: MkBlockQuote

```

</details>

</details>

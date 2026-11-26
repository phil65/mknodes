# MkDetailsBlock

[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github"> Show source on GitHub](https://github.com/phil65/mknodes/blob/main/src/mknodes/basenodes/mkdetailsblock/__init__.py)

### Pymdownx-based details box.

<details open>
<summary>Examples</summary>

### Example: **Regular**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "Different types." | MkDetailsBlock(typ="warning") }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkDetailsBlock(content='Different types.', typ='warning')
> ```

<details open>
<summary>Rendered</summary>

<details>
<summary>Warning</summary>

Different types.

</details>

</details>

<details>
<summary>Markdown</summary>

```markdown
<details>
<summary>Warning</summary>

Different types.

</details>

```

</details>

<details>
<summary>Html</summary>

```html
<details>
<summary>Warning</summary>
<p>Different types.</p>
</details>

```

</details>

<details>
<summary>GitHub</summary>

```markdown
<details>
<summary>Warning</summary>

Different types.

</details>

```

</details>

<details>
<summary>Repr tree</summary>

```
MkDetailsBlock
╰── MkText('Different types.')
```

</details>

### Example: **Collapsible and expandable**
> [!NOTE]
> **Jinja**
>
> ```jinja
> {{ "MkDetailsBlocks can also be expanded." | MkDetailsBlock(expanded=True) }}
>
> ```

> [!NOTE]
> **Python**
>
> ```python
> MkDetailsBlock(content='MkDetailsBlocks can also be expanded.', typ='info', expanded=True)
> ```

<details open>
<summary>Rendered</summary>

<details open>
<summary>Info</summary>

MkDetailsBlocks can also be expanded.

</details>

</details>

<details>
<summary>Markdown</summary>

```markdown
<details open>
<summary>Info</summary>

MkDetailsBlocks can also be expanded.

</details>

```

</details>

<details>
<summary>Html</summary>

```html
<details open>
<summary>Info</summary>
<p>MkDetailsBlocks can also be expanded.</p>
</details>

```

</details>

<details>
<summary>GitHub</summary>

```markdown
<details open>
<summary>Info</summary>

MkDetailsBlocks can also be expanded.

</details>

```

</details>

<details>
<summary>Repr tree</summary>

```
MkDetailsBlock
╰── MkText('MkDetailsBlocks can also be expanded.')
```

</details>

</details>

<details open>
<summary>DocStrings</summary>

<a id="mknodes.MkDetailsBlock"></a>

```python
class MkDetailsBlock(mkblock.MkBlock)
```

</details>

<details open>
<summary>Base classes</summary>

| Name | Children | Inherits |
|--- | --- | --- |
| **<font size='4'>[MkBlock](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkblock</font>*<br>PyMdown\-based block\. | <ul><li>[MkHtmlBlock](https://phil65.github.io/mknodes/)</li><li>[MkDetailsBlock](https://phil65.github.io/mknodes/)</li><li>[MkTabBlock](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[MkContainer](https://phil65.github.io/mknodes/)</li></ul> |

</details>

<details>
<summary>⋔ Inheritance diagram</summary>

```mermaid
graph TD
  3959722705["mkdetailsblock.MkDetailsBlock"]
  1483073837["mkblock.MkBlock"]
  835538629["mkcontainer.MkContainer"]
  1956333208["mkcontainer.MkContainerBase"]
  1359323199["mknode.MkNode"]
  2751680898["builtins.object"]
  1483073837 --> 3959722705
  835538629 --> 1483073837
  1956333208 --> 835538629
  1359323199 --> 1956333208
  2751680898 --> 1359323199
```

</details>

<details>
<summary>NodeFile</summary>

**/home/runner/work/mknodes/mknodes/src/mknodes/basenodes/mkdetailsblock/metadata.toml**

```toml
[metadata]
icon = "octicon:info-16"
name = "MkDetailsBlock"

[requirements.extension."pymdownx.blocks.details"]

[examples.regular]
title = "Regular"
jinja = """
{{ "Different types." | MkDetailsBlock(typ="warning") }}
"""

[examples.collapsible]
title = "Collapsible and expandable"
jinja = """
{{ "MkDetailsBlocks can also be expanded." | MkDetailsBlock(expanded=True) }}
"""

[output.markdown]
template = """
{{ node.fence_boundary }} details{% if node.argument %}" | " ~ {{ node.argument }}{% endif %}

    type: {{ node.typ }}
{% if node.expanded %}    open: True
{% endif %}

{{ node.get_items() | join }}
{{ node.fence_boundary }}

"""

```

</details>

<details>
<summary>Code</summary>

**mknodes.basenodes.mkdetailsblock.MkDetailsBlock**

```python
class MkDetailsBlock(mkblock.MkBlock):
    """Pymdownx-based details box."""

    ICON = "octicons/info-16"
    REQUIRED_EXTENSIONS = [resources.Extension("pymdownx.blocks.details")]
    STATUS = "new"

    def __init__(
        self,
        content: str | list | mk.MkNode | None = None,
        *,
        typ: datatypes.AdmonitionTypeStr = "info",
        expanded: bool | None = None,
        title: str | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructor.

        Args:
            content: Admonition content
            typ: Admonition type
            expanded: Whether the details block should be expanded initially
            title: Optional Admonition title
            kwargs: Keyword arguments passed to parent
        """
        super().__init__(
            "details",
            content=content or [],
            argument=title or "",
            attributes=dict(type=typ, open=expanded),
            **kwargs,
        )

    def __repr__(self) -> str:
        items = self.get_items()
        content = (
            reprhelpers.to_str_if_textnode(items[0])
            if len(items) == 1
            else [reprhelpers.to_str_if_textnode(i) for i in items]
        )
        return reprhelpers.get_repr(
            self,
            content=content,
            typ=self.typ,
            title=self.title,
            expanded=self.expanded,
            _filter_empty=True,
        )

    @property
    def title(self) -> str:
        return self.argument

    @title.setter
    def title(self, value: str) -> None:
        self.argument = value

    @property
    def typ(self) -> datatypes.AdmonitionTypeStr:
        return self.attributes["type"]

    @typ.setter
    def typ(self, value: datatypes.AdmonitionTypeStr) -> None:
        self.attributes["type"] = value

    @property
    def expanded(self) -> bool:
        return self.attributes["open"]

    @expanded.setter
    def expanded(self, value: bool) -> None:
        self.attributes["open"] = value

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
icon: octicons/info-16
status: new
title: MkDetailsBlock

```

</details>

</details>

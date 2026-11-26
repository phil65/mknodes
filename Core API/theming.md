# Theming

A build function receives the theme next to the root nav. [Theme](#mknodes.Theme) holds
the template overrides, CSS and the error page, [MaterialTheme](#mknodes.MaterialTheme)
adds Material for MkDocs settings (palette, colors, content width, status icons).

**Example**

```py
import mknodes as mk


def build(root: mk.MkNav, theme: mk.Theme) -> mk.MkNav:
    theme.error_page.content = mk.MkAdmonition("Page does not exist!")
    if isinstance(theme, mk.MaterialTheme):
        theme.content_area_width = 1300
    page = root.add_page("Home", is_index=True)
    page += "Hello"
    return root
```

## <a id="mknodes.Theme"></a>`mknodes.Theme`

```python
class Theme
```

MkDocs Theme.

## <a id="mknodes.MaterialTheme"></a>`mknodes.MaterialTheme`

```python
class MaterialTheme(theme.Theme)
```

Material Theme.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.api_section._add_page.<locals>._**

```python
@nav.route.page(title, hide="toc")
def _(page: mk.MkPage) -> None:
    page += INTROS[title]
    page += mk.MkCode(EXAMPLES[title].rstrip(), language="py", title="Example")
    for identifier in identifiers:
        page += mk.MkDocStrings(identifier, **DOCSTRING_OPTIONS)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/api_section.py
  source_function: _add_page.<locals>._
  source_line_no: 168
hide:
- toc
title: Theming

```

</details>

</details>

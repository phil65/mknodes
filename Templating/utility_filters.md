# Utility filters

The `jinja2` environment also contains some pre-defined filters.

> [!NOTE]
> The output gets passed to the first argument of the filter function.
> Filters are separated from the variable by a pipe symbol (|) and may have optional arguments in parentheses. Multiple filters can be chained. The output of one filter is applied to the next.

A base collection of filters is provided by [jinjarope](https://phil65.github.io/jinjarope)

Additional filters provided by MkNodes:

### `get_link`

Example:
```
"PageName" | get_link
```

<a id="mknodes.info.linkprovider.LinkProvider.get_link"></a>

```python
def get_link(target: LinkableType, title: str | None = None, from_page: mk.MkPage | None = None)
```

Return a markdown link for given target.

Target can be a class, a module, a MkPage, MkNav or a string.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `target` | `LinkableType` | The thing to link to |  |
| `title` | `str \| None` | The title to use for the link | None |
| `from_page` | `mk.MkPage \| None` | Page the link is for (to create relative links to own pages) | None |

### `get_url`

Example:
```
"PageName" | get_url
```

<a id="mknodes.info.linkprovider.LinkProvider.get_url"></a>

```python
def get_url(target: LinkableType) -> str
```

Get a url for given target.

Target can be a class, a module, a MkPage, MkNav or a string.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `target` | `LinkableType` | The thing to link to |  |

TODO

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.templating_section._**

```python
@nav.route.page("Utility filters")
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("templating/template_filters.jinja")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/templating_section.py
  source_function: _
  source_line_no: 50
title: Utility filters

```

</details>

</details>

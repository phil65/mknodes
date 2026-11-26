# Metadata

##Description

Every [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) as well as every [MkNav](../Core%20API/navs_and_pages.md#mknodes.MkNav) can carry metadata.
Page metadata inherits from Nav metadata, similarly as the **MkDocs-Material** meta plugin.

Metadata can be set either via the [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) constructor, via the [MkNav.route.page](../MkNavs/Using%20decorators/index.md#mknodes.navs.navrouter.NavRouter.page)
decorator. Also, some methods like [MkNav.parse.folder](../MkNavs/index.md#mknodes.navs.navparser.NavParser.folder) take metadata keyword arguments
in order to set it for all parsed pages.

## Examples

Via decorators:
`````py
@nav.route.page("My page", icon="material/code-json", status="new")
def _(page: mk.MkPage):
    ...
`````

Via constructor:
`````py
page = MkPage("My page", icon="material/code-json", status="new")
`````

## Metadata fields

<a id="mknodes.Metadata"></a>

```python
class Metadata
```

The Metadata class is a subclassed Python dictionary.

It is enhanced with properties for common metadata fields in order
to get proper type hints. Since this object is a dict subclass, you can of
course also add any non-documented stuff to the Metadata.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page(
    "Metadata",
    status="deprecated",
    search_boost=2.0,
    subtitle="Subtitle",
    description="Description",
)
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("pages/page_metadata.jinja")

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/page_section.py
  source_function: _
  source_line_no: 43
description: Description
search:
  boost: 2.0
status: deprecated
subtitle: Subtitle
title: Metadata

```

</details>

</details>

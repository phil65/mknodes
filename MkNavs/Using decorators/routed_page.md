# Routed page

> [!NOTE]
> I'm a page added via decorators!

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.routing.routed_page**

```python
@nav.route.page("Routed page")
def routed_page(page: mk.MkPage) -> None:
    """Builds a MkPage and attaches it to the router MkNav."""
    page += mk.MkAdmonition("I'm a page added via decorators!")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/routing.py
  source_function: routed_page
  source_line_no: 16
title: Routed page

```

</details>

</details>

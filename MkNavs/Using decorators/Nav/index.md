# Nav

> [!NOTE]
> You can also use decorators to attach MkNavs. These navs then can continue
> to build the tree without using decorators (by adding sub-navs).

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.routing.routed_nav**

```python
@nav.route.nav("Routed", "Deeply", "Nested", "Nav")
def routed_nav(nav: mk.MkNav) -> None:
    """Builds a nested MkNav and attaches it to the router MkNav."""
    index_page = nav.add_page(is_index=True)
    index_page += mk.MkAdmonition(NAV_TEXT)
    page = nav.add_page("Routed section page")
    page += mk.MkAdmonition("Routed section page content")

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
  source_function: routed_nav
  source_line_no: 28
title: Nav

```

</details>

</details>

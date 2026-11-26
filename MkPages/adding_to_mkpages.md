# Adding to MkPages

> [!NOTE]
> You can add other MkNodes to a page sequentially.

Adding strings also works, they get converted to MkText nodes.

### ...and text starting with # will become a MkHeader.

Every MkPage has a MkFootNotes node built-in[^1].

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page("Adding to MkPages", hide="toc", status="new")
def _(page: mk.MkPage) -> None:
    page += mk.MkAdmonition("You can add other MkNodes to a page sequentially.")
    page += "Adding strings also works, they get converted to MkText nodes."
    page += "### ...and text starting with # will become a MkHeader."
    page += "Every MkPage has a MkFootNotes node built-in[^1]."
    page.footnotes[1] = "Super cool, right?"

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/page_section.py
  source_function: _
  source_line_no: 34
hide:
- toc
status: new
title: Adding to MkPages

```

</details>

</details>

[^1]:
    Super cool, right?

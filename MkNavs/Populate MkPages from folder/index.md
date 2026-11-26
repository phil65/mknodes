# Populate MkPages from folder

## Directory tree

```
📂 `test_folder`
┣━━ 📝 `markdown-exec.md (507 Bytes)`
┗━━ 📝 `sub_1.md (286 Bytes)`
```

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.navs_section._**

```python
@nav.route.nav("Populate MkPages from folder")
def _(nav: mk.MkNav) -> None:
    """Create a MkNav based on a folder tree containing markup files."""
    folder = paths.TEST_RESOURCES / "nav_tree/test_folder/"
    nav.parse.folder(folder, hide="toc")
    page = nav.add_page(is_index=True, hide="toc", icon="folder")
    variables = dict(folder=folder)
    page += mk.MkTemplate("navs/nav_from_folder.jinja", variables=variables)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'pymdownx.highlight': {'anchor_linenums': True,
                                                      'line_spans': '__span',
                                                      'pygments_lang_class': True},
                               'pymdownx.superfences': {}},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/navs_section.py
  source_function: _
  source_line_no: 33
hide:
- toc
icon: material/folder
title: Populate MkPages from folder

```

</details>

</details>

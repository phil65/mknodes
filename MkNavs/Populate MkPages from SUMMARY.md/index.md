# Populate MkPages from SUMMARY.md

MkNavs can parse index files in `SUMMARY.md` style (as popularized by **mkdocs-literate-nav**).

Given the following folder structure:

> [!NOTE]
> **Directory tree**
>
> ```
> 📂 `nav_tree`
> ┣━━ 📂 `test_folder`
> ┃   ┣━━ 📝 `markdown-exec.md (507 Bytes)`
> ┃   ┗━━ 📝 `sub_1.md (286 Bytes)`
> ┣━━ 📂 `test_subnav`
> ┃   ┣━━ 📝 `subnav_page_1.md (132 Bytes)`
> ┃   ┣━━ 📝 `subnav_page_2.md (1.7 kB)`
> ┃   ┗━━ 📝 `SUMMARY.md (72 Bytes)`
> ┣━━ 📝 `SUMMARY.md (162 Bytes)`
> ┗━━ 📝 `test_file.md (55 Bytes)`
> ```

and a root `SUMMARY.md` looking like:

> [!NOTE]
> **Root SUMMARY.md**
>
> ```python
> * Test nested
>     * [General] (test_folder/sub_1.md)
>     * [Markdown-Exec] (test_folder/markdown-exec.md)
> * [Test Subnav] (test_subnav/)
> * [Test file] (test_file.md)
>
> ```

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.navs_section._**

```python
@nav.route.nav("Populate MkPages from SUMMARY.md")
def _(nav: mk.MkNav) -> None:
    folder = paths.TEST_RESOURCES / "nav_tree/"
    summary_file = folder / "SUMMARY.md"
    nav.parse.file(summary_file, hide="toc")
    page = nav.add_page(is_index=True, hide="toc", icon="file")
    text = summary_file.read_text("utf-8")
    text = text.replace("](", "] (")
    path = paths.TEST_RESOURCES / "nav_tree/"
    variables = dict(path=path, text=text)
    page += mk.MkTemplate("navs/nav_from_file.jinja", variables=variables)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'admonition': {},
                               'pymdownx.details': {},
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
  source_line_no: 20
hide:
- toc
icon: material/file
title: Populate MkPages from SUMMARY.md

```

</details>

</details>

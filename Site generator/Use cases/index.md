# Use cases

There are a lot of different ways **MkNodes** can be used to generate
websites. This section will highlight some of them.

**MkNodes** can be used in many different ways

* Create complete websites
    * **MkNodes** can be used to create a whole website (like it is done with this page)
      The most useful setup probably would be to put the whole navigation into code,
      create MkCodes via code when the complexity favours that, and otherwise just
      use `MkPage.from_file` or `MkTemplate` to embed static pages. That way
      you can get the best of both worlds, the simplicity from writing markdown files
      combined with the possibilities of using python for repititive work or
      more complex / dynamic tasks.

* Load existing markdown content and extend it.
    * By using `MkNav.parse.folder` / `MkNav.parse.file` as well as `MkPage.from_file`,
      the existing Markdown pages can become part of our tree
      (which we can then extend programatically). You dont need to start from ground
      up if you have an existing documentation.

* Create a subsection with **MkNodes** and reference it from your "static" page.
    * You can also create an **MkNodes** tree and reference that tree from your
      `nav:` section in `mkdocs.yml`.

* Create single static pages / blocks for your page
    You can also just use **MkNodes** to create some Nodes, stringify them and include
    the markdown in your static pages. It can also be used to create your **GitHub** / **PyPi**
    overview page.

* Using **Markdown-Exec** or similar inline execution plugins
    You can also embed **MkNodes** code directly by using various plug-ins
    (personal recommendation: **Markdown-Exec**) For most cases the built-in
    **jinja2** environment should include enough to display complex Markdown in an easy way.

* Create "multi-pages"
  **MkNodes** can even "merge" multiple websites into one.
  In its core, **MkNodes** is nothing more than one large tree ranging from the start page
  down to individual markdown elements.
   It is very easy to make a complete website tree the subtree of another Parent-tree.

  * Create a "structure template" for multiple sites
   **MkNodes** separates content and appearance for writing documentation. Website templates
   can be written in a way that they work for multiple websites without any manual adaption.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.site.use_cases_section._**

```python
@nav.route.page(is_index=True, hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/use_cases_index.jinja")

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/use_cases_section.py
  source_function: _
  source_line_no: 8
hide:
- toc
title: Use cases

```

</details>

</details>

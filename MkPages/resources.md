# Resources

All **MkNodes** can have "resources", which describe what is needed for the node to work.

This can include:

* CSS / JavaScript (either remote links or included in MkNodes)
* Markdown extensions including their specific config, if required
* Required python packages
* Plugins
* Additional asset files (images, ...)

If a template for a [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) was set, then the PageTemplate also is included as a resource for the [MkPage](../Core%20API/navs_and_pages.md#mknodes.MkPage) itself.

These resources are collected during the build phase and put into the appropriate places.
These places can be:

* Config file
* Build folder
* The HTML file the node is included in, by creating / modifying the page template.

Using this mechanism is optional, it is still possible to include the resources directly.
Inferred resources and directly included resources will get merged then.

<details>
<summary>Info</summary>

This mechanism only works when **MkNodes** "knows" about the nodes you used. That is the case when adding **MkNodes** directly to the tree as Python object, or by applying them as **jinja2** filters / macros using the [MkTemplate](../The%20nodes/Base%20nodes/mktemplate.md#mknodes.MkTemplate) node. In both cases, the resources get collected.
What *won't* work: Adding markdown in text form as an [MkText](../The%20nodes/Base%20nodes/mktext.md#mknodes.MkText) node which needs resources, or when using [MkPage.from_file](../Core%20API/navs_and_pages.md#mknodes.MkPage) for example. **MkNodes** is not a parser, so it cant know which extensions etc. your Markdown needs in order to get rendered correctly. In that case you have to add the required extensions etc manually to the **MkDocs** config, like you did before.

</details>

As examples, you can check the "Page information" box on all websites of this documentation.
It will show the required resources for given page.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page("Resources")
def _(page: mk.MkPage) -> None:
    page += mk.MkTemplate("resources.jinja")

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
  source_line_no: 73
title: Resources

```

</details>

</details>

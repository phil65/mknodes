# MkNode

[<img src="https://api.iconify.design/fa-brands/github.svg?height=16" alt="github"> Show source on GitHub](https://github.com/phil65/mknodes/blob/main/src/mknodes/basenodes/mknode/__init__.py)

### Base class for everything which can be expressed as Markup.

> [!NOTE]
> **Description**
>
>
> This class combines tree node functionality with markdown generation.
> Starting from the root nav (aka Docs) down to nested Markup blocks,
> the whole project can be represented by one tree.
>
> MkNode is the base class for all nodes. We dont instanciate it directly.
> All subclasses carry an MkAnnotations node (except the MkAnnotations node itself)
> They can also pass an `indent` as well as a `shift_header_levels` keyword argument
> in order to modify the resulting markdown.

<details open>
<summary>DocStrings</summary>

<a id="mknodes.MkNode"></a>

```python
class MkNode
```

</details>

<details open>
<summary>Sub classes</summary>

| Name | Children | Inherits |
|--- | --- | --- |
| **<font size='4'>[MkContainerBase](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkcontainer</font>*<br>Abstract base class for nodes containing other MkNodes\. | <ul><li>[MkContainer](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkCompactAdmonition](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkcompactadmonition</font>*<br>Compact admonition info box\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkLink](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mklink</font>*<br>A simple Link \(with optional icon and option to show up as a button\)\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkText](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mktext</font>*<br>Class for any Markup text\. | <ul><li>[MkInclude](https://phil65.github.io/mknodes/)</li><li>[MkChangelog](https://phil65.github.io/mknodes/)</li><li>[MkLicense](https://phil65.github.io/mknodes/)</li><li>[MkLlm](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[TemplateRenderMixin](https://phil65.github.io/mknodes/)</li><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkHeader](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkheader</font>*<br>Super simple header node\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkKeys](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkkeys</font>*<br>Node to display Keyboard keys\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkDocStrings](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes._mkdocstrings</font>*<br>Docstring section \(powered by mkdocstrings\)\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkIcon](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkicon</font>*<br>Pyconify\-based Icon\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkImage](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkimage</font>*<br>Image including optional caption\. | <ul><li>[MkBinaryImage](https://phil65.github.io/mknodes/)</li><li>[MkBadge](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkProgressBar](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkprogressbar</font>*<br>Node to display a CSS\-based progress bar\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[BaseBlock](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.pages.templateblocks</font>*<br>A class representing a block from a page template\. | <ul><li>[HtmlBlock](https://phil65.github.io/mknodes/)</li><li>[Block](https://phil65.github.io/mknodes/)</li><li>[TitleBlock](https://phil65.github.io/mknodes/)</li><li>[BaseJSBlock](https://phil65.github.io/mknodes/)</li><li>[StylesBlock](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkTimelineItem](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mktimeline</font>*<br>Single Timeline item / card\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkPyodideTerminal](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkpyodide</font>*<br>Node for embedding a Pyodide terminal running Python code\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkJupyterLite](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkjupyterlite</font>*<br>Node for embedding a JupyterLite RetroLab interface\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkPyScript](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkpyscript</font>*<br>Node for embedding a PyScript terminal\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkDataClassInfo](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.basenodes.mkdataclassinfo</font>*<br>Node for displaying dataclass\-like object information\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkNav](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.navs.mknav</font>*<br>Nav section, representing a nestable menu\. | <ul><li>[MkDoc](https://phil65.github.io/mknodes/)</li><li>[MkCliNav](https://phil65.github.io/mknodes/)</li><li>[MkDefaultWebsite](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkTemplateTable](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.templatenodes.mktemplatetable</font>*<br>Node for a table showing dependencies for a package\. | <ul><li>[MkClassTable](https://phil65.github.io/mknodes/)</li><li>[MkDependencyTable](https://phil65.github.io/mknodes/)</li><li>[MkModuleTable](https://phil65.github.io/mknodes/)</li></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[MkPyDeps](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.templatenodes.mkpydeps</font>*<br>Node for showing a Dependency graph\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |
| **<font size='4'>[FlavorComparison](https://phil65.github.io/mknodes/)</font>**<br>*<font size='1'>mknodes.manual.flavors</font>*<br>Markdown of a node in the Material and the GitHub flavour, side by side\. | <ul></ul> | <ul><li>[MkNode](https://phil65.github.io/mknodes/)</li></ul> |

</details>

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.nodes_section.create_section_for_nodes**

```python
def create_section_for_nodes(
    nav: mk.MkNav,
    klasses: Sequence[type[mk.MkNode]],
) -> mk.MkTable:
    table = mk.MkTable(columns=["Node", "Docstrings", "Markdown extensions"])
    for kls in klasses:
        tpl = "classpage_custom.jinja"
        page = mk.MkClassPage(kls, icon=kls.ICON, template_path=tpl, parent=nav, hide="toc")
        nav += page
        if kls.STATUS:
            page.metadata.status = kls.STATUS
        elif kls.JS_FILES:
            page.metadata.status = "js"
        elif kls.CSS:
            page.metadata.status = "css"
        page.created_by = create_section_for_nodes
        link = mk.MkLink(page, kls.__name__, icon=kls.ICON)
        extensions = ", ".join(f"`{i}`" for i in kls.REQUIRED_EXTENSIONS)
        table.add_row((link, kls.__doc__, extensions))
    return table

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'admonition': {},
                               'pymdownx.details': {},
                               'pymdownx.superfences': {},
                               'tables': {}},
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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/nodes_section.py
  source_function: create_section_for_nodes
  source_line_no: 93
hide:
- toc
icon: material/puzzle-outline
title: MkNode

```

</details>

</details>

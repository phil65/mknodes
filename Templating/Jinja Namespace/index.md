# Jinja Namespace

When a website build is started, **MkNodes** will collect as much information as possible
about the context by inspecting the distribution info, the local git repository, the remote GitHub repository as well as other project-related information. That information is used to build a context. A large amount of **MkNodes** fallback to context info if no other info is explicitely set, thus enabling the nodes to display project information without explicitely "hardcoding" the project.

### These are the available namespaces available in the Jinja2 environment:

<dl>
<dt>`metadata`</dt>
<dd>

Package information

</dd>
<dt>`git`</dt>
<dd>

Local repository information

</dd>
<dt>`github`</dt>
<dd>

Information about the remote repository

</dd>
<dt>`theme`</dt>
<dd>

Information about the theme being used

</dd>
</dl>

*Take a look at the sections in the site nav in order to discover all available information in the environment.*

The collected information is also used to populate the **MkNodes**-specific **Jinja2** namespace. In combination with the **MkNodes** jinja filters, this allows to efficiently write documentation about your project as well as building project-agnostic websites / website parts which can be re-used across different projects.

> [!NOTE]
> **Rendering CSS files**
>
> Data about the used theme (colors etc.) is also part of the context / project information.
> That information is used then to dynamically create CSS stylesheets during the build process.

#### Example:

This call would pass the module of the current context to **MkPipDepTree** and let it create a dependency graph:

``` py
{ { metadata.module | MkPipDepTree(direction="LR") } }
```

<details>
<summary>Page info</summary>

<details>
<summary>Code for this section</summary>

**mknodes.manual.templating_section._**

```python
@nav.route.nav("Jinja Namespace")
def _(nav: mk.MkNav) -> None:
    def add_context_doc(container: mk.MkPage, context: Any) -> None:
        container += mk.MkDocStrings(
            context,
            show_root_toc_entry=False,
            show_if_no_docstring=True,
            heading_level=4,
            show_bases=False,
            show_source=False,
        )

    for ctx in CONTEXTS:
        subpage = nav.add_page(ctx.__name__)
        add_context_doc(subpage, ctx)
    page = nav.add_page(is_index=True, hide="toc")
    variables = dict(namespaces=NAMESPACES)
    template = "templating/template_namespace_index.jinja"
    page += mk.MkTemplate(template, variables=variables)

```

</details>

<details>
<summary>Resources</summary>

```python
Resources(css=[],
          markdown_extensions={'def_list': {}},
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
  source_line_no: 29
hide:
- toc
title: Jinja Namespace

```

</details>

</details>

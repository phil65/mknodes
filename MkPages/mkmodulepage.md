# MkModulePage

**TODO: THIS NODE ISNT READY FOR PRIMETIME YET**

An **MkModulePage** is an **MkPage** subclass used to display information
about a specific module. It uses a Jinja template to display the module-related
information. By default, the Docstrings and tables showing the contained classes and
submodules. The template can be adjusted manually in case a different layout is
preferred.

<a id="mknodes.MkModulePage"></a>

```python
class MkModulePage(mktemplatepage.MkTemplatePage)
```

Page showing information about a module.

This is an example for an **MkModulePage** with the default layout, applied to `mknodes.info`:

# info

## Class info

### 🛈 DocStrings

<a id="mknodes.info"></a>

Information/Metadata- related classes.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.page_section._**

```python
@nav.route.page("MkModulePage")
def _(page: mk.MkPage) -> None:
    from mknodes import info

    variables = dict(example_module=info)
    page += mk.MkTemplate("pages/mkmodulepage.jinja", variables=variables)

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
  source_line_no: 21
title: MkModulePage

```

</details>

</details>

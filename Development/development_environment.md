# Development environment

All development for this library happens in the
[mknodes](https://github.com/phil65/mknodes.git) repo on GitHub.
First, you'll need to download the source code and install an
editable version of the Python package:

```md
# Clone the repository
git clone https://github.com/phil65/mknodes.git
cd mknodes
```

## Build system

Uv is used as the build system.

```bash
pip install uv
```

[More information](https://docs.astral.sh/uv/concepts/build-backend/)

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.dev_section._**

```python
@nav.route.page("Development environment", icon="dev-to")
def _(page: mk.MkPage) -> None:
    page += mk.MkDevEnvSetup()

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/dev_section.py
  source_function: _
  source_line_no: 13
icon: material/dev-to
title: Development environment

```

</details>

</details>

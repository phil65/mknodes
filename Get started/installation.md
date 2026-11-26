# Installation

### pip

The latest released version is available at the [Python package index](https://pypi.org/project/mknodes).

```python
pip install mknodes
```
### pipx

[pipx](https://github.com/pypa/pipx) allows for the global installation of Python applications in isolated environments.

```python
pipx install mknodes
```

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.get_started_section._**

```python
@nav.route.page("Installation", hide="toc", icon="grommet-icons:install")
def _(page: mk.MkPage) -> None:
    page += mk.MkInstallGuide()

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/get_started_section.py
  source_function: _
  source_line_no: 33
hide:
- toc
icon: grommet-icons:install
title: Installation

```

</details>

</details>

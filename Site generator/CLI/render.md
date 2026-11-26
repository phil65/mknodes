# render

## render

Render a single markdown file with Jinja macros.

Reads markdown content, processes Jinja templates, and outputs the result.

Example:
    mknodes render -i template.md -o output.md
    cat template.md | mknodes render -i - > output.md

```python
mknodes render [OPTIONS]
```

### `--input`, `-i`

"**REQUIRED**"
Input markdown file to render (use - for stdin).

### `--output`, `-o`

**Default:** -
Output file (use - for stdout, default).

### `--repo-url`, `-r`

Repository URL of the target package. Can be remote or local.

### `--verbose`, `-v`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Enable verbose output. (`DEBUG` level)

### `--quiet`, `-q`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Suppress output.

### `--help`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Show this message and exit.

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.site.cli_section._**

```python
@nav.route.page("render", icon="file-document")
def _(page: mk.MkPage):
    page += mk.MkCliDoc(CLI_PATH, prog_name="render")

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
          assets=[Asset('materialbadge_31c4bf6.css')],
          packages=[])
```

</details>

<details>
<summary>Metadata</summary>

```yaml
created:
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/cli_section.py
  source_function: _
  source_line_no: 31
icon: material/file-document
title: render

```

</details>

</details>

# render-folder

## render-folder

Render a folder of markdown files with Jinja macros.

Processes all files matching the glob pattern through Jinja templating,
preserving directory structure. Non-matching files can optionally be copied as-is.

Example:
    mknodes render-folder -i ./src/docs -o ./docs
    mknodes render-folder -i ./templates -o ./output --glob "**/*.md" --no-copy-other

```python
mknodes render-folder [OPTIONS]
```

### `--input`, `-i`

"**REQUIRED**"
Input directory containing files to render.

### `--output`, `-o`

"**REQUIRED**"
Output directory for rendered files.

### `--repo-url`, `-r`

Repository URL of the target package. Can be remote or local.

### `--glob`, `-g`

**Default:** **/*.md
Glob pattern for files to render as Jinja templates.

### `--copy-other`

**Default:** True
<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Copy files not matching the glob pattern as-is.

### `--workers`, `-w`

Number of parallel workers for copying files.

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
@nav.route.page("render-folder", icon="folder")
def _(page: mk.MkPage):
    page += mk.MkCliDoc(CLI_PATH, prog_name="render-folder")

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
  source_line_no: 36
icon: material/folder
title: render-folder

```

</details>

</details>

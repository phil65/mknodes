# serve

## serve

Serve a MkNodes-based website, locally or remotely.

This is `mknodes generate --watch` running next to the engine's server
(`zensical serve -f <generated config>`, http://localhost:8000/;
`mdbook serve <book dir>`, http://localhost:3000/; Docsify: a static file server,
http://localhost:3000/; Sphinx: `sphinx-autobuild`).

Further info here: https://phil65.github.io/mknodes/CLI/

```python
mknodes serve [OPTIONS]
```

### `--repo-url`, `-r`

Repository URL of the target package. Can be remote or local.

### `--build-fn`, `-b`

Path to the build script. (form: `path.to.module:function` )

### `--clone-depth`, `-c`

Git clone depth in case repository is remote. Important for changelog generation.

### `--config-path`, `-p`

**Default:** mkdocs.yml
Path to the config file.

### `--engine`, `-e`

**Default:** zensical
Site engine: `zensical` (HTML site, default), `mkdocs` (HTML site, needs the `mkdocs` extra), `mdbook` (HTML book, needs the `mdbook` binary to build / serve), `sphinx` (HTML site from MyST Markdown, needs the `sphinx` extra), `docsify` (Markdown rendered in the browser, no build step) or `markdown` (plain Markdown files).

### `--flavor`

Markdown flavour (`material`, `github`, `mdbook`, `myst`). Default: the engine's flavour (zensical / mkdocs: `material`, mdbook: `mdbook`, sphinx: `myst`, docsify / markdown: `github`).

### `--jinja-engine`

Template engine for the Jinja templates: `jinja2` (default) or `minijinja` (needs the `minijinja` extra). Default: `jinja_engine` of [tool.mknodes], else the MKNODES_JINJA_ENGINE environment variable, else jinja2.

### `--offline`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Take external inputs (icons, licenses, LLM texts) only from the lock file (`mknodes.lock`): fail if one is missing, never write the lock file.

### `--refresh-inputs`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Fetch all external inputs again and rewrite the lock file with exactly the used ones.

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
@nav.route.page("serve", icon="web")
def _(page: mk.MkPage):
    page += mk.MkCliDoc(CLI_PATH, prog_name="serve")

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
  source_line_no: 21
icon: material/web
title: serve

```

</details>

</details>

# generate

## generate

Generate the site input (pages, nav, assets, config) for the site engine.

Runs the build function (`mknodes.site:parse` / the default website unless
configured in `[tool.mknodes]` of `pyproject.toml` or in the `mknodes` entry of the
`plugins` list of `mkdocs.yml`) and writes the generated pages into the docs dir plus
a generated config (`mkdocs.generated.yml`) inheriting from `mkdocs.yml`.
Build afterwards with `zensical build -f mkdocs.generated.yml`
(`mkdocs build -f ...` for `--engine mkdocs`). `--engine mdbook` writes a book folder
(`book/`: `book.toml`, `src/`), `--engine sphinx` a Sphinx project (`sphinx/`:
`conf.py`, MyST pages), `--engine docsify` a Docsify site (`index.html`,
`_sidebar.md`), `--engine markdown` plain Markdown + `SUMMARY.md`.

```python
mknodes generate [OPTIONS]
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

### `--generated-dir`

Folder for generated pages (default: the docs dir).

### `--watch`, `-w`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Keep running and regenerate when project sources change.

### `--strict`, `-s`

<img src="https://api.iconify.design/mdi/flag.svg?height=16" alt="flag"> <code>Flag</code>
Strict mode: fail if the build reported problems (failed nodes, `/// mknodes` or `python exec` blocks, broken code fences, unresolved references). Also passed to the engine. Default: the `strict` setting.

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
@nav.route.page("generate", icon="file-tree")
def _(page: mk.MkPage):
    page += mk.MkCliDoc(CLI_PATH, prog_name="generate")

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
  source_line_no: 26
icon: material/file-tree
title: generate

```

</details>

</details>

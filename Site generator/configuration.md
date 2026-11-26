# Configuration

Settings are read from (later sources win):

1. the `mknodes` entry of the `plugins` list in `mkdocs.yml` (kept for existing sites),
2. `[tool.mknodes]` in `pyproject.toml` (**preferred**, `-` and `_` are interchangeable),
3. CLI options (`--build-fn`, `--repo-url`, `--clone-depth`, `--generated-dir`, ...).

Without any settings, the default website gets generated.

``` toml
[tool.mknodes]
build-fn = "docs/build.py:build"
show-page-info = true
global-resources = false
strict = true  # fail on build diagnostics (failed nodes / blocks, broken fences, references)
```

> [!NOTE]
> MkNodes writes HTML template overrides (announcement bars, per-page resources, the error
> page, ...) into the theme `custom_dir` (default: `overrides`). That folder must be placed
> outside of the `docs/` dir. Generated files are listed in a `.gitignore` inside the
> folders they get written to, hand-written files are never overwritten.

Available settings:

<a id="mknodes.site.settings.GeneratorSettings"></a>

```python
class GeneratorSettings
```

Settings for generating a website from a MkNodes build function.

#### <a id="mknodes.site.settings.GeneratorSettings.build_fn"></a>`build_fn`

```python
build_fn: str = paths.DEFAULT_BUILD_FN
```

Build function (`module:callable`, `path/file.py:callable`, `module:Class.method`).

#### <a id="mknodes.site.settings.GeneratorSettings.clone_depth"></a>`clone_depth`

```python
clone_depth: int = 100
```

Clone depth for remote repositories.

#### <a id="mknodes.site.settings.GeneratorSettings.config_file"></a>`config_file`

```python
config_file: pathlib.Path | None = None
```

The site config the generated config inherits from (`mkdocs.yml`).

#### <a id="mknodes.site.settings.GeneratorSettings.docs_dir"></a>`docs_dir`

```python
docs_dir: str | None = None
```

Docs folder (default: `docs_dir` of the site config, else `docs`).

#### <a id="mknodes.site.settings.GeneratorSettings.docsify"></a>`docsify`

```python
docsify: dict[str, Any] = dataclasses.field(default_factory=dict)
```

Extra `window.$docsify` options for the `docsify` engine (deep-merged into the
generated ones, e.g. `themeColor`, `subMaxLevel`).

#### <a id="mknodes.site.settings.GeneratorSettings.flavor"></a>`flavor`

```python
flavor: str | None = None
```

Markdown flavour of the generated pages (`material`, `github`, `mdbook`, `myst`).

Defaults to the flavour of the engine: `material` for `zensical` and `mkdocs`,
`mdbook` for `mdbook`, `github` for `markdown` and `docsify`, `myst` for `sphinx`.

#### <a id="mknodes.site.settings.GeneratorSettings.generated_config"></a>`generated_config`

```python
generated_config: str = GENERATED_CONFIG
```

Filename of the generated site config (relative to the project dir).

#### <a id="mknodes.site.settings.GeneratorSettings.generated_config_path"></a>`generated_config_path`

```python
generated_config_path: pathlib.Path
```

#### <a id="mknodes.site.settings.GeneratorSettings.generated_dir"></a>`generated_dir`

```python
generated_dir: str | None = None
```

Folder to write generated pages into (default: `docs_dir`).

If it differs from `docs_dir`, hand-written pages get mirrored into it and it becomes
the docs dir of the generated config. For `mdbook`: the book folder (default `book`),
for `sphinx`: the Sphinx source folder (default `sphinx`), for `docsify`: the site
folder (default: `site_dir`).

#### <a id="mknodes.site.settings.GeneratorSettings.global_resources"></a>`global_resources`

```python
global_resources: bool = True
```

Put CSS / JS into the site config instead of per-page template blocks.

#### <a id="mknodes.site.settings.GeneratorSettings.input_store"></a>`input_store`

```python
input_store: InputStore
```

The store for external inputs (configured lock file / mode), one per settings.

Shared by the generator (nodes) and the writer (page icons).

#### <a id="mknodes.site.settings.GeneratorSettings.inputs_mode"></a>`inputs_mode`

```python
inputs_mode: str = 'live'
```

How external inputs get resolved: `live` (lock file first, fetch + add missing
ones), `refresh` (fetch all again, prune unused lock entries) or `offline` (lock
file only, missing inputs are an error).

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_block_end_string"></a>`jinja_block_end_string`

```python
jinja_block_end_string: str | None = None
```

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_block_start_string"></a>`jinja_block_start_string`

```python
jinja_block_start_string: str | None = None
```

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_engine"></a>`jinja_engine`

```python
jinja_engine: str | None = None
```

Template engine for the Jinja templates: `jinja2` or `minijinja` (needs the
`minijinja` extra). Default: the `MKNODES_JINJA_ENGINE` environment variable, else
`jinja2`. See `jinjarope.engine` for the differences.

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_extensions"></a>`jinja_extensions`

```python
jinja_extensions: list[str] | None = None
```

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_loaders"></a>`jinja_loaders`

```python
jinja_loaders: list[dict[str, Any]] | None = None
```

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_variable_end_string"></a>`jinja_variable_end_string`

```python
jinja_variable_end_string: str | None = None
```

#### <a id="mknodes.site.settings.GeneratorSettings.jinja_variable_start_string"></a>`jinja_variable_start_string`

```python
jinja_variable_start_string: str | None = None
```

#### <a id="mknodes.site.settings.GeneratorSettings.kwargs"></a>`kwargs`

```python
kwargs: dict[str, Any] = dataclasses.field(default_factory=dict)
```

Keyword arguments for the build function (`pages` for the default build function).

#### <a id="mknodes.site.settings.GeneratorSettings.lock_file"></a>`lock_file`

```python
lock_file: str = 'mknodes.lock'
```

Lock file for external inputs (icons, licenses, LLM texts), relative to the project
dir. Empty: no lock file. See `mknodes.inputs`.

#### <a id="mknodes.site.settings.GeneratorSettings.lock_path"></a>`lock_path`

```python
lock_path: pathlib.Path | None
```

#### <a id="mknodes.site.settings.GeneratorSettings.mdbook"></a>`mdbook`

```python
mdbook: dict[str, Any] = dataclasses.field(default_factory=dict)
```

Extra `book.toml` content for the `mdbook` engine (deep-merged into the generated
config, e.g. `output.html.default-theme`). A `preprocessor.admonish` entry switches
admonitions to the `mdbook-admonish` syntax.

#### <a id="mknodes.site.settings.GeneratorSettings.project_dir"></a>`project_dir`

```python
project_dir: pathlib.Path = dataclasses.field(default_factory=pathlib.Path.cwd)
```

Root folder of the project (contains `mkdocs.yml` / `pyproject.toml`).

#### <a id="mknodes.site.settings.GeneratorSettings.render_by_default"></a>`render_by_default`

```python
render_by_default: bool = True
```

Render generated pages with the MkNodes Jinja environment.

#### <a id="mknodes.site.settings.GeneratorSettings.repo_path"></a>`repo_path`

```python
repo_path: str = '.'
```

Repository to build docs for (local path or remote URL).

#### <a id="mknodes.site.settings.GeneratorSettings.resolved_docs_dir"></a>`resolved_docs_dir`

```python
resolved_docs_dir: pathlib.Path
```

#### <a id="mknodes.site.settings.GeneratorSettings.resolved_generated_dir"></a>`resolved_generated_dir`

```python
resolved_generated_dir: pathlib.Path
```

#### <a id="mknodes.site.settings.GeneratorSettings.show_page_info"></a>`show_page_info`

```python
show_page_info: bool = False
```

Append a collapsible box with build info to every page.

#### <a id="mknodes.site.settings.GeneratorSettings.site_config"></a>`site_config`

```python
site_config: dict[str, Any] = dataclasses.field(default_factory=dict, repr=False)
```

The loaded site config (`INHERIT` resolved, custom tags preserved).

#### <a id="mknodes.site.settings.GeneratorSettings.site_dir"></a>`site_dir`

```python
site_dir: str | None = None
```

Output folder for the HTML build (default: the site config's `site_dir`).

#### <a id="mknodes.site.settings.GeneratorSettings.sphinx"></a>`sphinx`

```python
sphinx: dict[str, Any] = dataclasses.field(default_factory=dict)
```

`conf.py` settings for the `sphinx` engine: `theme` (`html_theme`, default `furo`),
`extensions` (added to `myst_parser` / `sphinx_design`); any other key becomes a
`conf.py` variable (e.g. `html_theme_options`, `suppress_warnings`).

#### <a id="mknodes.site.settings.GeneratorSettings.strict"></a>`strict`

```python
strict: bool = False
```

Fail the build if it reported problems (build diagnostics).

Counted are: nodes which failed to get created in templates, failing `/// mknodes`
blocks and `python exec="true"` blocks (they render their error into the page),
broken code fences and unresolved `[title][identifier]` references. Without strict
mode they get logged as warnings. Also passed to the engine (`zensical build --strict`).

#### <a id="mknodes.site.settings.GeneratorSettings.theme_config"></a>`theme_config`

```python
theme_config: dict[str, Any]
```

#### <a id="mknodes.site.settings.GeneratorSettings.__init__"></a>`__init__`

```python
def __init__(project_dir: pathlib.Path = pathlib.Path.cwd(), config_file: pathlib.Path | None = None, build_fn: str = paths.DEFAULT_BUILD_FN, kwargs: dict[str, Any] = dict(), repo_path: str = '.', clone_depth: int = 100, show_page_info: bool = False, render_by_default: bool = True, global_resources: bool = True, strict: bool = False, flavor: str | None = None, docs_dir: str | None = None, generated_dir: str | None = None, lock_file: str = 'mknodes.lock', inputs_mode: str = 'live', generated_config: str = GENERATED_CONFIG, site_dir: str | None = None, mdbook: dict[str, Any] = dict(), docsify: dict[str, Any] = dict(), sphinx: dict[str, Any] = dict(), jinja_engine: str | None = None, jinja_loaders: list[dict[str, Any]] | None = None, jinja_extensions: list[str] | None = None, jinja_block_start_string: str | None = None, jinja_block_end_string: str | None = None, jinja_variable_start_string: str | None = None, jinja_variable_end_string: str | None = None, site_config: dict[str, Any] = dict()) -> None
```

#### <a id="mknodes.site.settings.GeneratorSettings.get_builder"></a>`get_builder`

```python
def get_builder() -> Callable[..., Any]
```

Return the build function with the configured kwargs bound.

#### <a id="mknodes.site.settings.GeneratorSettings.get_jinja_config"></a>`get_jinja_config`

```python
def get_jinja_config() -> jinjarope.EnvConfig
```

#### <a id="mknodes.site.settings.GeneratorSettings.load"></a>`load`

```python
def load(project_dir: str | os.PathLike[str] | None = None, config_file: str | os.PathLike[str] | None = None, **overrides: Any) -> GeneratorSettings
```

Load settings for given project.

**Parameters:**

| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `project_dir` | `str \| os.PathLike[str] \| None` | Project root (default: cwd, or the folder of `config_file`) | None |
| `config_file` | `str \| os.PathLike[str] \| None` | Site config to read (default: `mkdocs.yml` in the project dir) | None |
| `overrides` | `Any` | Explicit setting overrides (`None` values are ignored) | {} |

<details>
<summary>Page info</summary>

<details>
<summary>Code for this page</summary>

**mknodes.manual.site._**

```python
@nav.route.page("Configuration", hide="toc")
def _(page: mk.MkPage):
    page += mk.MkTemplate("site/configuration.jinja")
    page += mk.MkDocStrings(
        "mknodes.site.settings.GeneratorSettings",
        show_root_toc_entry=False,
        show_if_no_docstring=True,
        heading_level=4,
        show_bases=False,
        show_source=False,
    )

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
  source_filename: /home/runner/work/mknodes/mknodes/src/mknodes/manual/site/__init__.py
  source_function: _
  source_line_no: 21
hide:
- toc
title: Configuration

```

</details>

</details>

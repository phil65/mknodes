# AGENTS.md

## Overview

MkNodes is a Python library for building documentation as a tree of objects ("nodes") that
render to Markdown/HTML with the resources they need (CSS, JS, Markdown extensions). Nodes
can be created from Python or from Jinja templates (every node is also a Jinja filter). It also
contains the site generator (`mknodes build` / `serve` / `generate`, formerly the separate
`mkdocs-mknodes` package) used by ~36 docs sites (built with Zensical), so keep the public API
(`import mknodes as mk; mk.MkXyz`) and the `[tool.mknodes]` settings stable.
Since 3.0 MkNodes is site-engine agnostic: `mkdocs` / `mkdocs-material` are not runtime
dependencies and must not be imported by library code (`MkPluginFlow` was removed).

## Architecture

- `src/mknodes/__init__.py`: public API; re-exports every node class (`mk.MkPage`, `mk.MkNav`, ...).
- `basenodes/mknode/__init__.py`: `MkNode`, the base class. Tree handling (parent/children,
  `iter_nodes`), `ctx` (project context), `env` (Jinja env), `to_markdown()`, `get_resources()`,
  `to_html()`. Most rendering is async.
- `basenodes/`: primitive nodes (`mktext`, `mkadmonition`, `mkcode`, `mktable`, `mkcontainer`, ...).
  Each node is a package with `__init__.py` plus a `metadata.toml` ("node file", parsed by
  `info/nodefile.py`) holding metadata, required extensions/CSS, examples (`python`/`jinja`) and
  reference `output` templates. `basenodes/processors/` holds text post-processors.
- `templatenodes/`: higher-level nodes built from project info (`mkchangelog`, `mkshields`,
  `mkinstallguide`, `mkdependencytable`, `mkllm`, `mktemplate`, ...).
- `extranodes/`: nodes not exported from `mknodes` (`mkcodeimage`, `mkgrid`, `mksnippet`, ...).
- `pages/`: `MkPage` (`mkpage.py`), `MkClassPage`, `MkModulePage`, page `Metadata`,
  `PageTemplate` / template blocks.
- `navs/`: `MkNav` (`mknav.py`), `MkDoc` (auto API docs), `MkCliNav`, `Router` (`router.py`,
  decorator-based routing: `nav.route.page(...)`), `navparser.py` (SUMMARY.md / folder parsing).
- `info/`: project introspection: `contexts.py` (`ProjectContext`, `PackageContext`,
  `GitContext`, `ThemeContext`, ...), `folderinfo.py`, `packageinfo.py`, `gitrepository.py`,
  `pyproject.py`, `linkprovider.py`, registries for packages/repos/griffe.
- `jinja/`: `NodeEnvironment` (`nodeenvironment.py`, a `jinjarope.Environment` exposing all nodes
  as filters/globals) and `filters.py`. Registered as `jinjarope.environment` entry point.
  Nodes created by a template are collected **per render** (`NodeEnvironment.render_nodes[_async]()`
  -> `RenderResult(markdown, nodes, children, resources)`, collector in a context variable; nested
  renders of the same env add to the outer one). `{{ node }}` is awaited in the running loop via
  `NodeCodeGenerator` (hooks Jinja's private `_output_child_pre/_post`: re-check on Jinja updates)
  instead of `str(node)` -> `run_sync`. Template nodes (`MkTemplate`, `MkTemplatePage`,
  `MkTemplateTable`, `MkText(render_jinja=True)`) use `jinja/rendercache.TemplateRenderMixin`:
  one render per flavour serves children and content; setting an attribute drops the cache,
  in-place mutation (e.g. `node.variables["x"] = 1`) does not. `env.rendered_nodes` /
  `rendered_children` are deprecated (last render only).
- `theme/`: `Theme`, `MaterialTheme` (palette, colors, status icons).
- `build/`: tree -> engine-neutral output. `DocBuilder` (`builder.py`): renders every page in
  a flavour (`flavor=`), page info box, wires page templates (`pagetemplates.py`, also moves
  per-page CSS / JS into templates with `global_resources=False`), turns resources (+ theme
  resources / templates / extras) into `assets`, `extra_css`, `extra_javascript`,
  `markdown_extensions`, `templates` and the nav into a `NavItem` tree (`output.py`
  `BuildOutput`). Sequential unless `max_workers > 1`. `MarkdownExporter` (`exporter.py`) writes
  pages + assets + `SUMMARY.md`.
- `site/`: the site generator. Layering: core modules never import `mknodes.site` / `mknodes.cli`
  (`tests/test_layering.py`).
  - `settings.py` `GeneratorSettings`: read from the `mknodes` entry of the `plugins` list in
    `mkdocs.yml` (existing sites have `- mknodes` there; zensical ignores it), then
    `[tool.mknodes]` in `pyproject.toml` (preferred, `-`/`_` interchangeable), then CLI options.
    Unknown keys are ignored. Docstrings are shown on the manual's "Configuration" page.
  - `generator.py` `SiteGenerator`: theme, `ProjectContext.for_project()` (the only context
    factory), runs the build fn, `DocBuilder(flavor=...).build(root, theme)`, then URL collision
    renames (safety net) and bare `[x](file.md)` link fixing (needs docs_dir's hand-written files).
  - Build fn contract: `build_fn(root=..., theme=..., **kwargs)` (kwargs from settings), sync or
    async, mutates `root`. Paths: `module:callable`, `path/file.py:callable`,
    `module:Class.classmethod`. Default `mknodes.site:parse`: with `pages` setting the nav is
    parsed (`navs/navparser.py`, example `resources/site/pages_example.toml`), else
    `defaultsite.populate_default_website()` (README index, API docs, CLI page, Development nav).
  - `writers/`: `Writer` base (`flavor`, `write()`, `build_command()` / None = no build step),
    `GeneratedFolder` manifest (`docs/.gitignore`; hand-written files are never overwritten; old
    `mkdocs-mknodes` manifests are still recognized), `ZensicalWriter` (docs dir + template
    overrides into `custom_dir` + `mkdocs.generated.yml` with `INHERIT: mkdocs.yml`),
    `MarkdownWriter` (engine `markdown`, GitHub flavour, `MarkdownExporter` files).
  - `yamlconfig.py` (YAML round-trip keeping `!ENV` / `!!python/name` tags, `INHERIT`),
    `watch.py` (polling watcher, regenerates in a subprocess via `python -m mknodes generate`).
- `cli/`: Typer app `mknodes` (`app.py`, rich logging via `richstate.py`); `site.py`: `build`,
  `serve`, `generate` (`--engine zensical|markdown`, `--flavor`); `render.py`: `render`,
  `render-folder`. Entry point `cli:main` (configures logfire).
- `rendering/`: Markdown flavours. A `Renderer` (`base.py`) per flavour holds rules
  (node type -> `async def rule(node, renderer) -> str`, registered with
  `@GithubRenderer.rule(mk.MkAdmonition)`). Lookup walks the node MRO: Python rule, then an
  `[output.<template_key>]` template of the class's `metadata.toml`, and stops at a class
  that renders itself (`get_content` / `to_md_unprocessed`); no rule -> the node renders
  itself, which is Material flavour (`MaterialRenderer`, the default, has no rules).
  The active renderer is a context variable (`rendering.use()`, `node.to_markdown(flavor=)`,
  `DocBuilder(flavor=)`); containers render children with `rendering.current().render_child()`
  so nested nodes and `{{ node }}` in Jinja keep the flavour. `github.py`: GitHub flavour
  (alerts, `<details>`, `<kbd>`, Iconify `<img>` icons, title heading instead of front matter).
  `apidocs.py`: API docs from Griffe objects (for flavours without mkdocstrings; GitHub's
  `MkDocStrings` rule). `materialtext.py`: converts hand-written Material blocks (`!!!`, `???`,
  `===`) in page text; GitHub runs it as a page processor.
- `mdext/`: Python-Markdown extensions (`/// mknodes` blocks, `execute_ext` for
  `python exec="true"` blocks, `codeinclude`); `- mknodes.mdext` in mkdocs.yml. See `mdext/README.md`.
- `data/`: static data (admonition types, badges, build systems, tools, task runners, ...).
- `utils/`: helpers (`resources.py` resource model, `icons.py`, `classhelpers.py`,
  `linkreplacer.py`, `log.py`, ...). `resources/`: bundled CSS/JS/inventory files.
- `manual/`: the project's own documentation, written with mknodes. Entry point
  `manual/root.py:Build.build`, sections in `manual/*_section.py`. Uses Jinja templates
  from `docs/` (loaded via `contexts.DEFAULT_LOADER = FileSystemLoader("docs")`).

Flow: build function populates a root `MkNav` -> nodes resolve context (`ctx`) ->
`DocBuilder` renders each page in a flavour (renderer rules / `to_markdown()`, Jinja) and
collects `Resources` -> `BuildOutput` -> `MarkdownExporter` (plain files) or a site
writer (zensical: docs dir + `mkdocs.generated.yml`).

## Where to look

| Task | Location |
| --- | --- |
| Add/change a node | `src/mknodes/basenodes/<node>/` or `templatenodes/<node>/` (code + `metadata.toml`), export in `src/mknodes/__init__.py` |
| Node examples / reference output | the node's `metadata.toml` (`[examples.*]`, `[output.markdown]`) |
| Jinja filters / env | `src/mknodes/jinja/` |
| Project metadata shown in docs | `src/mknodes/info/` |
| Navigation, routing, SUMMARY.md parsing | `src/mknodes/navs/` |
| Theme / palette | `src/mknodes/theme/` |
| CLI | `src/mknodes/cli/__init__.py` |
| Markdown extensions | `src/mknodes/mdext/` |
| Project docs content | `src/mknodes/manual/` + `docs/*.jinja` |
| Docs site config | `mkdocs.yml` (settings in the `mknodes` plugins entry: `build_fn: mknodes.manual.root:Build.build`) |
| Site generator settings / CLI / writers | `src/mknodes/site/`, `src/mknodes/cli/` |

## Commands

```bash
uv sync --all-extras                 # setup (CI uses this)
uv run pytest                        # tests (also run by the pre-commit hook)
uv run ruff check . && uv run ruff format --check .
uv run mypy src/                     # type checker (mypy, not ty)
uv run mknodes build -v         # docs build, as in documentation.yml
uv run pytest benchmarks/ --codspeed # benchmarks (codspeed.yml)
uv build
uv run duty lint | test | build | serve   # wrappers in duties.py
```

## Conventions

- Python >= 3.13, `from __future__ import annotations`, ruff (line length 100, Google docstrings).
- mypy is the type checker in CI and pre-commit; there is no ty setup.
- Rendering APIs are async (`await node.to_markdown()`, `await node.get_resources()`); tests use
  pytest-asyncio with `asyncio_mode = "auto"`.
- Tests live in `tests/`, one file per area. `tests/test_nodefiles.py` renders every node's
  `metadata.toml` examples, checks that `[output.markdown]` templates match `to_md_unprocessed()`,
  and snapshots per-node resources in `tests/snapshots/`; update with `uv run pytest --snapshot-update`
  only when a resource change is intended.
- Conventional commits (commitizen hook); allowed types in `[tool.mknodes]` in pyproject.

## Pitfalls

- Not copier-managed: pyproject, workflows and pre-commit config are edited by hand.
- Many nodes need network or external tools: icons come from the Iconify API via
  `jinjarope`/`pycons` (meant to be cached by anyenv in `~/.cache/anyenv`; 429 rate limits
  break docs builds and the `MkIcon` tests), `MkPyDeps` needs Graphviz (`dot`) and the dev-only
  `pydeps` package, `MkLlm` needs an LLM API key (`OPENAI_API_KEY` in CI), git-based nodes need
  a git checkout with history.
- Tests that run git must clear `GIT_*` env vars (the pre-commit hook runs pytest with
  `GIT_DIR`/`GIT_INDEX_FILE` set), see `tests/test_gitrepository.py`.
- New container-like nodes must render children via `rendering.current().render_child(item)`
  (not `item.get_content()` + `item.get_processors()`), otherwise flavours don't reach them.
  Threads don't inherit the active renderer: set it with `rendering.use()` inside the thread
  (`coroutines.run_sync` copies the context already).
- Container nodes (`MkContainerBase` subclasses) render via `get_content()`; a subclass that only
  overrides `to_md_unprocessed()` is detected by `_overrides_markdown_only()` in
  `basenodes/mkcontainer/__init__.py`. Check nested rendering (`page += node`) when adding nodes.
- Route functions (`@nav.route.page/nav`) run lazily and in parallel threads on first access
  (`Navigation._ensure_materialized`); their entries get re-sorted into declaration order
  afterwards. Generated output must be reproducible: no `id()`, no thread-order dependence.
- `MkDoc` (`navs/mkdoc.py`) only adds submodule navs with `recursive=True`. Which module
  documents which class is computed once per tree by `navs/apiscope.py` (`ApiScope`): every
  class gets one page below its defining module (`pkg.sub.Klass` -> `API/sub/Klass/`, module
  -> `API/sub/`), re-exports only link to it, private modules get no navs. Class page names keep
  their case; a clash with a sibling module folder / `index` gets a `-class` suffix, so API
  URLs can't collide. Class pages are registered in `ctx.links` (`register_object_page`), so
  `get_link` on a class / module yields a relative link to its page. Changing the scheme
  changes live URLs of all docs sites (minor release at least). `flatten_nav` has no effect.
- `mknodes.execute` (`mdext/execute_ext.py`) `auto_register` does not take effect; register the
  fences explicitly via `get_custom_fences()` in the superfences config.
- `MkTemplate` paths are relative to `docs/`; the manual breaks if templates move.
- Downstream users: many docs sites import node classes and helpers directly.
- `utils.log.get_logger(name)` returns loggers below `mknodes` (names outside the namespace get
  prefixed), so all output can be configured via the `mknodes` logger.
- Repositories without an `origin` remote work: `GitRepository.remote_url` falls back to the
  first remote, `repo_name` to the folder name; the package name then comes from pyproject.
- Generated files: `docs/.gitignore` / `overrides/.gitignore` are manifests written by the
  site generator; `mkdocs.generated.yml` is regenerated on every run.

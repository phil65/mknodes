# AGENTS.md

## Overview

MkNodes is a Python library for building documentation as a tree of objects ("nodes") that
render to Markdown/HTML with the resources they need (CSS, JS, Markdown extensions). Nodes
can be created from Python or from Jinja templates (every node is also a Jinja filter). It is
the engine behind the `mkdocs-mknodes` site generator (sites are built with Zensical) and ~30
docs sites, so keep the public API (`import mknodes as mk; mk.MkXyz`) stable.
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
- `theme/`: `Theme`, `MaterialTheme` (palette, colors, status icons).
- `build/`: `DocBuilder` (`builder.py`, walks a root `MkNav` and renders pages, optionally in
  parallel), `BuildOutput`, `MarkdownExporter`.
- `cli/__init__.py`: Typer CLI `mknodes` with `build`, `render`, `render-folder`.
- `mdext/`: Python-Markdown extensions (`/// mknodes` blocks, `execute_ext` for
  `python exec="true"` blocks, `codeinclude`); `- mknodes.mdext` in mkdocs.yml. See `mdext/README.md`.
- `data/`: static data (admonition types, badges, build systems, tools, task runners, ...).
- `utils/`: helpers (`resources.py` resource model, `icons.py`, `classhelpers.py`,
  `linkreplacer.py`, `log.py`, ...). `resources/`: bundled CSS/JS/inventory files.
- `manual/`: the project's own documentation, written with mknodes. Entry point
  `manual/root.py:Build.build`, sections in `manual/*_section.py`. Uses Jinja templates
  from `docs/` (loaded via `contexts.DEFAULT_LOADER = FileSystemLoader("docs")`).

Flow: build function populates a root `MkNav` -> nodes resolve context (`ctx`) -> each page
renders to Markdown via Jinja/`to_markdown()` and collects `Resources` -> `DocBuilder` /
`mkdocs-mknodes` writes files and a generated site config (`mkdocs.generated.yml`) -> zensical.

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
| Docs site config | `mkdocs.yml` (settings in the `mknodes` plugins entry: `build_fn: mknodes.manual.root:Build.build`, read by `mkdocs-mknodes`) |

## Commands

```bash
uv sync --all-extras                 # setup (CI uses this)
uv run pytest                        # tests (also run by the pre-commit hook)
uv run ruff check . && uv run ruff format --check .
uv run mypy src/                     # type checker (mypy, not ty)
uv run mkdocs-mknodes build --engine zensical -v   # docs build, as in documentation.yml
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
- Container nodes (`MkContainerBase` subclasses) render via `get_content()`; a subclass that only
  overrides `to_md_unprocessed()` is detected by `_overrides_markdown_only()` in
  `basenodes/mkcontainer/__init__.py`. Check nested rendering (`page += node`) when adding nodes.
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
- `src/mknodes/info/packageinfo.py` uses CRLF line endings; keep them.
- Downstream users: `mkdocs-mknodes` and many docs sites import node classes and helpers directly.
- `utils.log.get_logger(name)` returns loggers below `mknodes` (names outside the namespace get
  prefixed), so all output can be configured via the `mknodes` logger.
- Repositories without an `origin` remote work: `GitRepository.remote_url` falls back to the
  first remote, `repo_name` to the folder name; the package name then comes from pyproject.
- `uv run` re-syncs `mkdocs-mknodes` from PyPI; to test against a local checkout use
  `uv pip install -e ../mkdocs_mknodes` and `.venv/bin/mkdocs-mknodes build`.

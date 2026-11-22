# AGENTS.md

## Overview

MkNodes is a Python library for building documentation as a tree of objects ("nodes") that
render to Markdown/HTML with the resources they need (CSS, JS, Markdown extensions, MkDocs
plugins). Nodes can be created from Python or from Jinja templates (every node is also a Jinja
filter). It is the engine behind the `mkdocs-mknodes` MkDocs plugin and ~20 docs sites, so keep
the public API (`import mknodes as mk; mk.MkXyz`) stable: fixes only, no breaking changes.

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
`mkdocs-mknodes` writes files and merges resources into the MkDocs config.

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
| Docs site config | `mkdocs.yml` (`mknodes` plugin with `build_fn: mknodes.manual.root:Build.build`) |

## Commands

```bash
uv sync --all-extras                 # setup (CI uses this)
uv run pytest                        # tests (also run by the pre-commit hook)
uv run ruff check . && uv run ruff format --check .
uv run mypy src/                     # type checker (mypy, not ty)
uv run mkdocs-mknodes build          # docs build, as in documentation.yml
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
  `jinjarope`/`pycons` (cached by anyenv in `~/.cache/anyenv`; rate limits cause 429s),
  `MkPyDeps` needs Graphviz (`dot`) and the dev-only `pydeps` package, `MkLlm` needs an LLM API key (`OPENAI_API_KEY`
  in CI), git-based nodes need a git checkout with history.
- `MkTemplate` paths are relative to `docs/`; the manual breaks if templates move.
- `src/mknodes/info/packageinfo.py` uses CRLF line endings; keep them.
- Downstream users: `mkdocs-mknodes` and many docs sites import node classes and helpers directly.

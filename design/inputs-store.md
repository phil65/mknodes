# External inputs: inventory and inputs store

Phase 10 of the target direction (rendering = pure sync core, I/O = async shell). Step 1:
an inventory of every place where building pages does I/O or non-deterministic work, and
an inputs store (`ctx.inputs`) with a lock file that resolves external data before rendering.

## Part A: inventory (2026-11-26, mknodes 4.3.1)

Columns: where, node(s) / caller, what is fetched, key (what identifies the input),
cacheable (same key -> same value?), current caching. "Render time" means the work runs
while a node renders (inside `to_markdown()` / `get_content()`), "setup" means while the
project context or the tree gets created (before rendering), "writer" means after the
build, in a site writer.

### Network

| Where | Nodes / callers | Fetches | Key | Cacheable | Caching today | Phase |
| --- | --- | --- | --- | --- | --- | --- |
| `utils/iconcache.py` (`get_icon_svg[_async]`, via pycons -> api.iconify.design) | `MkIcon` (render), `MkBinaryImage.for_icon` (setup), `Theme.add_admonition_type`, `MaterialTheme.add_status_icon`, palette toggle icons via `utils/icons.get_icon_xml` (setup), Jinja global `get_icon_svg` (render), `site/writers/zensical.IconResolver` (writer: page / social icons) | icon SVG | icon spec + SVG params (color, size, flip, rotate, box) | yes (immutable per name) | on-disk cache `~/.cache/mknodes/icons` (`MKNODES_CACHE_DIR`), never expires, + memory | render / setup / writer |
| `templatenodes/mkllm` (`complete_llm` via agentpool) | `MkLlm` (render) | LLM completion | model, system prompt, user prompt, context (+ extra files) | no (non-deterministic), must be pinned | `anyio` in-process cache only; every build makes a paid call (CI: `OPENAI_API_KEY`) | render |
| `info/license.py` (`License.from_name`, SPDX db + details JSON from GitHub raw / spdx.org via anyenv) | `MkLicense(license_type=...)` (render), `FolderInfo.license_text` (setup, only without a license file; `run_sync`) | license text + metadata | SPDX id / name | yes (rarely changes) | anyenv HTTP cache (`~/.cache/anyenv`) | render / setup |
| `utils/downloadhelpers.download` / `pathhelpers.load_file_cached` (anyenv, any fsspec URL) | `MkInclude` (render), `MkText.from_url` (setup), Jinja `load_file` filter (jinjarope, render) | file content | URL / path | mostly (remote files change) | anyenv HTTP cache | render / setup |
| `utils/inventorymanager.Inventory.from_url` | `LinkProvider.add_inv_file` (setup; only the bundled stdlib inventory is loaded today, `ProjectContext.populate_linkprovider` is never called) | `objects.inv` | URL | mostly | anyenv HTTP cache | setup |
| `rendering/github.py` `icon_img` -> jinjarope `get_pyconify_key` -> pycons `api.collections()` | `MkIcon` in the GitHub / mdBook flavours (render) | Iconify collection list (prefix mapping) | - | mostly | anyenv HTTP cache; fails on a cold cache inside the build's event loop (anyio "Already running asyncio") | render |
| githarbor (`GitRepository.__init__` -> `githarbor.create_repository`) | `GitContext.repo_hoster`, `edit_uri` (setup) | GitHub repo + owner (PyGithub, 2 API calls) | repo URL | mostly | none | setup |
| `GitHubContext.from_url` (githarbor: workflows, user profile) | nothing (dead: `ctx.github` stays the empty default) | - | repo URL | - | - | - |
| `extranodes/mkcodeimage.for_file`, `MkBinaryImage.for_file` (fsspec) | setup | file bytes (local or URL) | path / URL | mostly | none | setup |
| badges (`data/badges.py`, `MkShields`, `MkMetadataBadges`) | render | nothing: only shields.io *URLs* (the browser fetches) | - | - | - | - |

Notes:
- **githarbor does nothing in practice**: no provider is installed in the dev / CI venv
  (`githarbor[github]` missing), `create_repository` raises, the error is suppressed and
  `repo_hoster` is `"Base"`, `edit_uri` `None`. With a provider installed, every context
  creation would make two GitHub API calls (rate limit 60/h without token).
- **No PyPI metadata is fetched anywhere.** Package metadata (`PackageContext`,
  `MkDependencyTable`, `MkInstallGuide`, ...) comes from `importlib.metadata` of the
  installed environment (see "Environment"). PyPI only appears as shields.io badge URLs.

### Subprocess / git

| Where | Nodes / callers | Runs | Key | Cacheable | Caching today | Phase |
| --- | --- | --- | --- | --- | --- | --- |
| `templatenodes/mkchangelog` (`git_changelog.build_and_render`, `asyncio.to_thread`) | `MkChangelog` (render) | `git log` + parse, Markdown changelog | repo path, template, convention, sections, filter-commits (+ HEAD) | per commit | `functools.cache` (process) | render |
| `info/gitrepository.py` (GitPython) | `GitContext` (`commits` = whole history, current sha / author / dates, last version tag), `version_changes` (setup) | `git rev-list`, `git log`, tags | repo path + HEAD | per commit | `cached_property` | setup |
| `info/reporegistry.py`, `mkdocsconfigfile` | `ProjectContext.for_project(<remote url>)` (setup) | `git clone --depth` | URL + depth | no | registry (process) | setup |
| `templatenodes/mkpydeps` (`pydeps` + Graphviz `dot`, `asyncio.to_thread`) | `MkPyDeps` (render; manual: only with `CI` set) | module dependency SVG | module path + options | per source | none | render |
| `templatenodes/mkcommandoutput` (Jinja `check_output` filter -> `subprocess.getoutput`) | `MkCommandOutput` (render; manual example only with `CI`) | command output | command + cwd | no | none | render |
| `mdext/execute_ext.py` (`exec`), `/// mknodes` blocks | engine process (Markdown extension) | arbitrary code | code | no | none | engine |

### Environment (installed packages, env vars)

| Where | Nodes / callers | Reads | Phase |
| --- | --- | --- | --- |
| `templatenodes/mkpipdeptree` (`pipdeptree`, `asyncio.to_thread`) | `MkPipDepTree` (render) | dependency tree of the installed environment | render |
| `info/packageinfo.py`, `packagehelpers.py` (`importlib.metadata`) | `PackageContext`, `MkDependencyTable`, `MkDependencyGroups`, `MkInstallGuide`, `MkCliDoc` (clinspector imports the CLI), `MkDocStrings` / `MkDoc` (griffe, local sources) | distribution metadata, entry points, module sources | setup / render |
| `os.environ` | `manual/nodes_section.py` (`CI` -> `MkPyDeps`), `MkCommandOutput` example (`getenv('CI')`), iconcache (`MKNODES_CACHE_DIR`), diagnostics file, agentpool (`OPENAI_API_KEY`), githarbor (`GITHUB_TOKEN`) | flags / secrets | setup / render |
| `MkLlm.extra_files` (fsspec) | `MkLlm` | context files (anywhere) | render |

### Time / date

| Where | What |
| --- | --- |
| `build/output.py` (`SiteMetadata.from_context`) | `Copyright © {datetime.now().year}` (default site copyright) |
| jinjarope globals `now()` / `utcnow()` | available in every template (the manual does not use them) |
| `GitContext.current_date_*` | from git (deterministic per commit) |

### Threads / `run_sync` / `to_thread`

`run_sync` call sites (10; 7 in node / render code):

| Where | Why |
| --- | --- |
| `basenodes/mknode` `__str__`, `__hash__`, `to_markdown` (3) | sync API over async rendering (`str(node)`: ~460 uses in node code, e.g. MkTable widths, MkCode) |
| `templatenodes/mktemplatetable` (1) | renders cells synchronously |
| `jinja/nodeenvironment.py` (1) | sync template render (`render_string` / `render_template`) |
| `pages/pagetemplate.py` `__hash__` (1, anyenv) | hash of rendered HTML |
| `navs/navigation.py` (1, anyenv) | async route functions |
| `info/folderinfo.py` `license_text` (1, anyenv) | network license lookup (above) |
| `site/generator.py` (2, anyenv) | entry points: async build fn, `DocBuilder.build` |

`asyncio.to_thread` in nodes (5): `MkChangelog`, `MkPipDepTree`, `MkPyDeps`, `MkBadge`
(anybadge: CPU only, deterministic, no I/O), iconcache. Thread pools: `DocBuilder`
(`max_workers`), `navigation.py` (parallel route functions), `cli/render.py`.

### Counts

| Kind | Sites | Of which at render time |
| --- | --- | --- |
| Network | 9 (icons, icon collection list, LLM, license, file download, inventories, githarbor, file-based images; GitHubContext dead) | 5 (MkIcon / Jinja icons, GitHub-flavour icon prefixes, MkLlm, MkLicense, MkInclude / `load_file`) |
| Subprocess / git | 6 (changelog, GitPython context, clone, pydeps, command output, exec) | 3 (MkChangelog, MkPyDeps, MkCommandOutput) |
| Environment | 4 | 2 (MkPipDepTree, griffe / clinspector-based nodes) |
| Time | 2 (+ git dates) | 1 (jinjarope `now`, unused) |
| `run_sync` | 10 call sites | 7 |

## Part B: inputs store (implemented, step 1)

Package `mknodes.inputs` (core; no `mknodes.site` imports).

- **Input kinds** (`InputKind`, `inputs.KINDS`, `register_kind`): one per kind of external
  data: `name` (lock-file namespace), `locked` (pinned in the lock file), `source` (shown
  in the lock file), `key_id(params)` (id of an input), async `fetch(params)` + `fetch_sync`,
  `available()` (e.g. optional extra installed). Values are JSON-serializable. Built in:

  | Kind | Locked | Key id | Used by |
  | --- | --- | --- | --- |
  | `icon` | yes | icon spec (+ `?param=value` for SVG params) | `MkIcon`, and every `iconcache.get_icon_svg[_async]` call during a build (themes, emoji index, Jinja `get_icon_svg`, `MkBinaryImage.for_icon`, zensical writer page / social icons) |
  | `license` | yes | SPDX id / name (lowercase) | `MkLicense(license_type=...)` |
  | `icon_prefixes` | yes | `collections` (one entry: all Iconify icon set prefixes) | `iconcache.get_pyconify_key` for specs without a prefix separator (`:fa-brands-github:`): GitHub / mdBook flavour `icon_img`, `icons.get_emoji_slug`, `icon_for_url` |
  | `file` | yes | remote URL (http(s) or another fsspec protocol) | `MkInclude`, `MkText.from_url`, the Jinja `load_file` filter, `MkCodeImage.for_file`, `MkTimeline` / `MkShowcase` item files, `MkPage.from_file`, everything reading via `pathhelpers.load_file[_cached]` (local paths stay unlocked) |
  | `binary_file` | yes | remote URL (value: base64) | `MkBinaryImage.for_file`, inventories (`Inventory.from_url`), `pathhelpers.load_bytes` |
  | `llm` | yes | `<model>:<sha256 of model + prompts + context>` | `MkLlm` |
  | `changelog` | no (local git, per commit) | params JSON | `MkChangelog` |
  | `pipdeptree` | no (installed environment) | params JSON | `MkPipDepTree` |
  | `pydeps` | no (local sources) | params JSON | `MkPyDeps` (pydeps + Graphviz `dot`) |
  | `command` | no (local environment) | params JSON (`call`, `cwd`) | `MkCommandOutput`, the Jinja `check_output` filter |

  Unlocked kinds are local and deterministic for a checkout / environment: resolved in the
  resolve phase like the others (concurrently, off the event loop), never written to the
  lock file, also computed in offline mode.

- **Requests**: `MkNode.get_input_requests()` (default `[]`) returns
  `InputRequest.create(kind, **params)`.
- **Resolve phase**: `DocBuilder._build` walks the tree (as before), collects the requests of
  all nodes (per store) and calls `await store.resolve(requests)`: missing inputs are fetched
  concurrently (`max_concurrency`, default 8) before any page renders. Failed fetches are
  logged and remembered (reading the input raises the error, no second try).
- **Reading**: `ctx.inputs.get(kind, **params)` (sync) / `await ctx.inputs.aget(...)`.
  Inputs which were not requested up front (nodes created while templates render, code
  without a node context) are fetched on demand and recorded too (`store.on_demand`), so
  the lock file covers them and offline works for them as well.
- **Active store**: `inputs.use_store(store)` / `inputs.active_store()` (process-wide, so
  worker threads see it). `SiteGenerator` activates the build's store for the whole build
  (+ the CLI for the writer) and points the fallback context (nodes outside the tree,
  e.g. rendered examples) at it. `iconcache.get_icon_svg[_async]` read from the active
  store; outside builds they use the on-disk cache directly (`fetch_icon_svg[_async]`).
- **Modes**: `live` (default: locked values first, fetch missing ones and add them;
  nothing gets pruned, so partial builds / tests can't shrink the file), `refresh`
  (re-fetch every input the build uses, the lock keeps exactly these), `offline` (lock file
  only: a missing locked input raises `MissingInputError`, listing all missing inputs in
  the resolve phase; the lock file is never written). Offline, a missing input of an
  unavailable kind (`MkLlm` without agentpool) raises `InputUnavailableError` instead and
  the node uses its placeholder.
- **Settings / CLI**: `lock_file = "mknodes.lock"` (`[tool.mknodes]`, relative to the
  project dir, `""` disables) and `inputs_mode`; `mknodes build | generate | serve` take
  `--offline` / `--refresh-inputs`. The CLI exits with the `MissingInputError` message
  (no traceback, also when a template wrapped it).
- **Lock file**: written after the build (and after the writer) if its content changed.
  Deterministic JSON (sorted keys, 2-space indent, UTF-8, trailing newline); entries of
  kinds unknown to this version are kept:

  ```json
  {
    "inputs": {
      "icon": {
        "mdi:file": {
          "fetched_at": "2026-11-26T07:00:00Z",
          "source": "api.iconify.design",
          "value": "<svg ...>"
        }
      }
    },
    "version": 1
  }
  ```

  The manual's lock file (`mknodes.lock`, committed) holds 16 icons, 1 license, the included
  README (`MkInclude` example) and the `MkLlm` example text (~57 KB). The LLM entry is a
  recorded placeholder (no paid calls by agents): `OPENAI_API_KEY=... uv run duty
  refresh-inputs` replaces it with a real completion (cheaper: delete the `llm` section and
  run `uv run mknodes generate`, live mode only fetches missing inputs).
- **CI** (`documentation.yml`): every engine build runs `--offline` (no network or LLM
  calls, no icon / HTTP caches, no `OPENAI_API_KEY`); a missing input fails the build with
  the `MissingInputError` list. `duty refresh-inputs` refreshes (and prunes) with the default
  engine, then generates the other engines in live mode, so inputs only used by other
  flavours stay in the lock file. Verified locally with sockets disabled and cold caches.
  The icon disk cache (`~/.cache/mknodes/icons`) stays as the second level behind the store.
- Tests: `tests/test_inputs.py` (resolve concurrency / dedup, lock round trip, live / refresh
  / offline, remembered failures, migrated nodes rendering from a lock file with network
  failing, builder resolve phase, active store, CLI `--offline`). `tests/conftest.py` gives
  every test a fresh fallback store and replaces `complete_llm` with a fake (the `MkLlm`
  node-file example renders while collecting tests: with `OPENAI_API_KEY` set this made a
  paid call on every test run before).

## Part C: pure sync rendering (step 2, 2026-11-26)

Rendering is synchronous and never fetches. Fetching (async, concurrent) only happens in
resolve steps between renders.

- **Remaining I/O moved to the store** (kinds above): pydeps, shell commands, remote files of
  any fsspec protocol (text + binary), `FolderInfo.license_text` (SPDX text without a license
  file, kind `license`), inventories. Code without a node context reads
  `inputs.get_input(kind, ...)` (`default_store()`: the active store, else a process-wide
  memory store).
- **Clock**: `utils.buildtime.build_time()` (once per process; `SOURCE_DATE_EPOCH` wins) for the
  default copyright year and the `now()` / `utcnow()` globals of node environments.
- **Render passes** (`inputs/passes.py`): inputs only known while rendering (nodes created by
  templates, the page Jinja pass, `iconcache.get_icon_svg`, Jinja `load_file` /
  `check_output`) used to be fetched in the middle of a render. Now every top-level render runs
  inside `inputs.render_pass()`: `store.get()` of a missing input records it in the pass and
  raises `InputPendingError`. `Renderer.render()` turns that into an empty render of that node
  and the tree walk skips the children of a template node that raised, so one pass finds all
  independent missing inputs. The pass is discarded together with the diagnostics it reported
  (`diagnostics.deferred()`), the recorded inputs get resolved, the template render caches
  dropped (`rendercache.invalidate_all()`) and the render runs again (max. 8 passes, then
  `PendingInputsError`). With a complete lock file: one pass.
  - DocBuilder: tree walk (request pass), declared inputs (`get_input_requests`) resolved
    concurrently, pages (each page its own pass: only pages which read a missing input render
    again), nav / theme resources and page templates.
  - SiteGenerator: the walk for the link excludes.
  - `to_markdown()` / `str(node)` / `get_resources()` at the top level; nested inside a
    render they just render.
  - Outside passes (setup, build functions, writers) `store.get()` still fetches on demand.
- **Sync API**: `to_markdown()` / `str(node)`, `get_resources()`, `to_html()`,
  `get_toc()`, `DocBuilder.build()`, `MarkdownExporter.export()`,
  `NodeEnvironment.render_nodes()` / `render_string()` / `render_template()`. Override points
  (`get_content`, `to_md_unprocessed`, `get_node_resources`, renderer rules) are sync.
  4.6 kept the async API as deprecated wrappers next to `*_sync` methods; 5.0 removed the
  wrappers and gave the sync methods the short names (no aliases).
- **Jinja**: environments are sync; `{{ node }}` compiles to `environment._render_output(node)`.
- **Threads**: no event loop / thread per node. `coroutines.run_sync` remains for resolve steps
  (one loop per step) and async user code (build / route functions). DocBuilder workers render
  pages in `contextvars.copy_context().run`. Kinds whose fetch touches process-wide state run
  under a lock: git-changelog (`redirect_stdout`), pipdeptree (not thread-safe), pydeps (chdir).
- Tests: `tests/test_inputs.py` (`test_rendering_does_no_io`: a build with inputs only found
  while rendering makes no socket connect / subprocess / fetch inside a render pass; discarded
  passes drop their diagnostics; top-level `str(node)` resolves first).

Not covered: jinjarope filters with I/O other than `load_file` / `check_output` (e.g.
`llm_complete`, `online()`): generic jinjarope, not used by mknodes templates. Setup-time git
(`GitContext`, GitPython) and githarbor (inert) stay at context creation. Route functions still
run in a thread pool (`navigation.py`, `_materialized` is set before they ran).

## Remaining I/O sites before step 2 (historical)

Not migrated (still I/O while building, bypassing the store):

- Render time: `MkText.from_url` / Jinja `load_file` (downloads), `MkPyDeps`
  (pydeps + dot), `MkCommandOutput` (Jinja `check_output`), `MkCodeImage.for_file` /
  `MkBinaryImage.for_file` (fsspec reads), griffe / clinspector based nodes (local sources,
  imports: deterministic, stay unlocked), `MkBadge` (CPU only, `to_thread`).
- Setup: `FolderInfo.license_text` (SPDX lookup via `run_sync` when there is no license
  file), `GitContext` / `GitRepository` (whole history, at context creation),
  githarbor in `GitRepository.__init__` (inert without a provider), remote clones,
  `LinkProvider.add_inv_file` (inventories).
- Time: default copyright year (`build/output.py`), jinjarope `now()` / `utcnow()`.
- Still async while rendering: nodes read with `await ctx.inputs.aget(...)`; with all inputs
  resolved up front, step 2 can switch them to `get` and make `get_content` sync. Nodes created
  while templates render are only known after the template ran (on-demand fetch today): step 2
  needs a request pass over templates (or a render-collect-resolve-render loop).
- `run_sync` call sites (10) unchanged.

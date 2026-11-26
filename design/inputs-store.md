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
| `basenodes/mknode` `__str__`, `__hash__`, `to_markdown_sync` (3) | sync API over async rendering (`str(node)`: ~460 uses in node code, e.g. MkTable widths, MkCode) |
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
| Network | 8 (icons, LLM, license, file download, inventories, githarbor, file-based images; GitHubContext dead) | 4 (MkIcon / Jinja icons, MkLlm, MkLicense, MkInclude / `load_file`) |
| Subprocess / git | 6 (changelog, GitPython context, clone, pydeps, command output, exec) | 3 (MkChangelog, MkPyDeps, MkCommandOutput) |
| Environment | 4 | 2 (MkPipDepTree, griffe / clinspector-based nodes) |
| Time | 2 (+ git dates) | 1 (jinjarope `now`, unused) |
| `run_sync` | 10 call sites | 7 |

## Part B: inputs store

Package `mknodes.inputs` (core; no `mknodes.site` imports).

- **Input kinds** (`InputKind`): one per kind of external data, with a `name` (lock-file
  namespace), whether it is `locked` (written to the lock file), a `source` (shown in the
  lock file), `key_id(params)` (the id under which the value is stored) and an async
  `fetch(params)` (+ `fetch_sync` for sync callers). Values are JSON-serializable.
  Registered in `inputs.KINDS`; built in:

  | Kind | Locked | Key id | Used by |
  | --- | --- | --- | --- |
  | `icon` | yes | icon spec (+ `?param=value` for SVG params) | `MkIcon` |
  | `license` | yes | SPDX id / name (lowercase) | `MkLicense(license_type=...)` |
  | `llm` | yes | sha256 of model + prompts + context | `MkLlm` |
  | `changelog` | no (local git, per commit) | params JSON | `MkChangelog` |
  | `pipdeptree` | no (installed environment) | params JSON | `MkPipDepTree` |

  Unlocked kinds are local and deterministic for a checkout / environment: they are
  resolved in the resolve phase like the others (concurrently, off the event loop), but
  never written to the lock file and also computed in offline mode.

- **Requests**: nodes declare what they need with `MkNode.get_input_requests()` (default:
  none), returning `inputs.InputRequest(kind, params)`.
- **Resolve phase**: `DocBuilder` walks the tree (as before), collects the requests of all
  nodes, and resolves the missing ones concurrently (`InputStore.resolve(requests)`,
  bounded by `max_concurrency`, default 8) before rendering any page. Failed fetches are
  remembered (the node gets the error when it reads the input, as before; no second try).
- **Reading**: nodes read with `ctx.inputs.get(kind, **params)` (sync) or
  `await ctx.inputs.aget(...)`. Inputs which were not requested (nodes created while
  templates render, migrated nodes outside a build) fall back to fetching on demand and
  get recorded as well, so the lock file covers them too.
- **Modes** (`InputStore.mode`): `live` (default: use locked values, fetch missing ones,
  add them to the lock file; nothing gets pruned), `refresh` (re-fetch every input used
  by the build, rewrite the lock file with exactly these: prunes unused entries),
  `offline` (only the lock file: a missing locked input raises `MissingInputError`; the
  lock file is never written).
- **Lock file**: `mknodes.lock` in the project dir (setting `lock_file`, `""` disables;
  CLI `build` / `generate` / `serve` take `--offline` and `--refresh-inputs`). Written
  after the build if it changed. Deterministic JSON (sorted keys, 2-space indent):

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

- Where it lives: `ProjectContext.inputs` (default: an in-memory store in live mode, so
  nodes outside the site generator work as before). `SiteGenerator` creates the store
  from the settings and saves it after the build.

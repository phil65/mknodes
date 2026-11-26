# Project metadata: distribution, import packages, repository

How mknodes finds out what it documents (`ctx.metadata`), before and after mknodes 4.5.0.

## Before (mknodes <= 4.4.1)

The model assumed "repository name == distribution name == import name, one top-level
module". Resolution chain for `mknodes build` / `generate`:

1. `SiteGenerator.create_context` -> `ProjectContext.for_project(project_dir or repo_path)`
   -> `reporegistry.get_repo()` (clones remote URLs) -> `FolderInfo(working_dir)`.
2. `FolderInfo._module_name`: the **git repository name** (last part of the `origin` remote
   URL, else the folder name) if there is a remote, else `[project.name]`; mapped to a module
   with `epregistry.distribution_to_package(name, fallback=True)` (installed
   `packages_distributions()` mapping, else `-` -> `_`).
   -> clawd-code-sdk (repo `claude-agent-sdk-python`) imported `claude_agent_sdk_python`,
   which doesn't exist; a fork or a renamed folder changed the documented package.
3. `FolderInfo.module` / `griffe_module`: `importlib.import_module(_module_name)` (must be
   installed). `ctx.metadata.module` is what `MkDoc` (API docs) documents by default.
4. `FolderInfo.info`: `packageregistry.get_info([project.name] or repo name)` -> `PackageInfo`
   on the **installed** distribution (`importlib.metadata.distribution`); not installed ->
   `PackageNotFoundError`, no docs.
5. Repository URL: mkdocs `repo_url` -> git remote -> installed `Project-URL` (`Source`,
   `Repository`, `Source Code`). Username / repo name parsed from a GitHub URL.
6. `PackageInfo.urls` parsed `Project-URL: Label, URL` by splitting on the first comma:
   a label with a comma (`Spec: Claude Agent SDK (Python, upstream)`) yielded the URL
   `upstream)`; `icons.icon_for_url` then took `netloc.split(".")[-2]` of an empty netloc
   -> `IndexError` while building `social_info`.
7. Default site (`mknodes.site:parse`): one `API` section for `ctx.metadata.module`; other
   top-level modules of the distribution were not documented. The reference check validated
   `distribution_name.replace("-", "_")` only. The PyPI social link used the module name.

## After (mknodes 4.5.0)

Three independent names, resolved by `mknodes.info.projectlayout.ProjectLayout`
(`FolderInfo.layout`):

- **Distribution**: `[project.name]` (fallback: the repository name). Metadata from the
  installed distribution (`importlib.metadata`), else synthesized from `pyproject.toml`
  (`packageinfo.PyProjectDistribution`: name, version, summary, readme, authors, license,
  classifiers, URLs, dependencies, extras, entry points), so a project builds without being
  installed.
- **Import packages**: all top-level modules the distribution ships. First source with a
  result wins:
  1. `[tool.mknodes] packages = [...]`,
  2. build backend config: uv_build `module-name` (str or list; default: normalised
     distribution name) + `module-root` (default `src`); hatch
     `[tool.hatch.build.targets.wheel] packages`; setuptools `packages` (list or
     `packages.find` with `where` / `include` / `exclude`), `py-modules`, `package-dir`;
     flit `module.name`; poetry `packages` (`include` / `from`); maturin `module-name` /
     `python-source`,
  3. the installed distribution: `top_level.txt`, else the top-level entries of its files,
  4. a scan of `src/` (src layout; namespace packages and single-file modules included) or of
     the project folder (flat layout; folders with `__init__.py`, minus `tests`, `docs`, ...).

  Dotted names (`ns.pkg`) are kept for packages below a namespace package. A package which is
  not importable gets imported from its source folder (`ImportPackage.import_module` puts the
  import root on `sys.path`).
- **Primary package**: `[tool.mknodes] package = "..."`, else the package matching the
  normalised distribution name (`fake.src-proj` -> `fake_src_proj`), else the first one.
  It is `ctx.metadata.module` / `griffe_module` / `package_name`; `ctx.metadata.package_names`
  lists all (primary first).
- **Repository**: mkdocs `repo_url` -> `[project.urls]` (`Source`, `Repository`,
  `Source Code`, `Code`, `GitHub`) -> git remote -> installed metadata. Independent of the
  package names; `repository_username` / `repository_name` come from the URL.

Uses of the model:

- Default site: one package -> `API` section as before (URLs unchanged); several packages ->
  `API` with one sub-section per package (`API/<package>/...`), packages which fail to
  import are skipped with a warning.
- Reference check: validates the top-level names of all import packages.
- Social links: PyPI link uses the distribution name. `icons.icon_for_url(url, default=None)`
  never raises (unparsable URLs, hosts without a dot, unknown hosts -> `default`); the social
  links skip URLs without an icon, as before. `Project-URL` values get split on the last
  `", "` (labels may contain commas).

Settings (`[tool.mknodes]` in `pyproject.toml`):

| Key | Meaning |
| --- | --- |
| `package` | Primary import package (default: the one matching the distribution name, else the first) |
| `packages` | Explicit list of import packages (overrides build backend / installed / scan) |

Verified on (2026-11-26): mknodes (manual output unchanged), clawd-code-sdk
(`clawd-code-sdk` / `clawd_code_sdk` / `phil65/claude-agent-sdk-python`), agentpool
(11 packages from the uv_build `module-name` list; `agentpool_sync` in `src/` is not shipped
and not documented).

Known limits: `GitRepository` needs a git checkout (`FolderInfo` of a folder without `.git`
fails); `PackageInfo.entry_points` / CLI detection use `epregistry` and need an installed
distribution.

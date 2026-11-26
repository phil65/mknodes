"""Project layout: distribution, import packages and repository of a project.

The three names of a project are independent of each other:

- the **distribution** (`[project.name]`, what gets installed: `clawd-code-sdk`),
- the **import packages** (the top-level modules the distribution ships: `clawd_code_sdk`;
  a distribution can ship several, like `agentpool`, `agentpool_config`, ...),
- the **repository** (where the code is hosted: `phil65/claude-agent-sdk-python`).

Import packages get resolved from (first source with a result wins):

1. `[tool.mknodes] packages = [...]` (explicit list),
2. the build backend config (uv_build `module-name` / `module-root`, hatch wheel
   `packages`, setuptools `packages` / `packages.find` / `py-modules`, flit `module.name`,
   poetry `packages`, maturin `module-name` / `python-source`),
3. the installed distribution (`top_level.txt`, else the top-level entries of its files),
4. a scan of `src/` (src layout) or of the project folder (flat layout).

The primary package is `[tool.mknodes] package`, else the one matching the normalised
distribution name, else the first one.
"""

import dataclasses
import fnmatch
import importlib
from importlib import metadata
import pathlib
import re
import sys
from typing import TYPE_CHECKING, Any, Literal

from mknodes.utils import log


if TYPE_CHECKING:
    from collections.abc import Iterable, Mapping
    import types


logger = log.get_logger(__name__)

PackageSource = Literal[
    "tool.mknodes",
    "uv_build",
    "hatch",
    "setuptools",
    "flit",
    "poetry",
    "maturin",
    "installed",
    "scan",
]

# Folders of a project root which are never import packages (flat layout scan).
NON_PACKAGE_DIRS = frozenset({
    "tests",
    "test",
    "testing",
    "docs",
    "doc",
    "benchmarks",
    "examples",
    "scripts",
    "tools",
    "build",
    "dist",
    "site",
    "overrides",
    "typings",
    "node_modules",
})

# `[project.urls]` keys (case-insensitive) pointing to the code repository, by priority.
REPOSITORY_URL_KEYS = ("source", "repository", "source code", "code", "github")


def normalize_name(name: str) -> str:
    """Return the import name a distribution name maps to by convention (PEP 503 + `_`)."""
    return re.sub(r"[-_.]+", "_", name).lower()


@dataclasses.dataclass(frozen=True)
class ImportPackage:
    """A top-level module (or namespace subpackage) shipped by the distribution."""

    name: str
    """Import name (dotted for packages below a namespace package: `ns.pkg`)."""
    path: pathlib.Path | None = None
    """Source location in the project (package folder or `.py` file), if known."""
    source: PackageSource = "scan"
    """Where the package was found."""

    @property
    def is_namespace(self) -> bool:
        """Whether the package is a namespace package (a folder without `__init__.py`)."""
        p = self.path
        return p is not None and p.is_dir() and not (p / "__init__.py").exists()

    @property
    def import_root(self) -> pathlib.Path | None:
        """The folder which has to be on `sys.path` to import the package."""
        if self.path is None:
            return None
        return self.path.parents[len(self.name.split(".")) - 1]

    def import_module(self) -> types.ModuleType:
        """Import the package; from its source folder if it is not importable otherwise."""
        try:
            return importlib.import_module(self.name)
        except ModuleNotFoundError as e:
            root = self.import_root
            missing = e.name or ""
            ours = self.name == missing or self.name.startswith(f"{missing}.")
            if not ours or root is None or not root.is_dir():
                raise
            logger.info("Importing %s from %s (not installed)", self.name, root)
            sys.path.insert(0, str(root))
            importlib.invalidate_caches()
            return importlib.import_module(self.name)


@dataclasses.dataclass
class ProjectLayout:
    """Distribution name, import packages and layout of a project folder."""

    path: pathlib.Path
    """Project root."""
    distribution: str
    """Distribution name (`[project.name]`)."""
    packages: list[ImportPackage] = dataclasses.field(default_factory=list)
    """All import packages of the distribution (primary first)."""
    layout: Literal["src", "flat", "unknown"] = "unknown"
    """Source layout of the project."""

    @property
    def primary(self) -> ImportPackage | None:
        """The main import package (documented first, used for `ctx.metadata.module`)."""
        return self.packages[0] if self.packages else None

    @property
    def package_names(self) -> list[str]:
        return [p.name for p in self.packages]

    @classmethod
    def resolve(
        cls,
        path: str | pathlib.Path,
        pyproject: Mapping[str, Any],
        *,
        fallback_name: str = "",
    ) -> ProjectLayout:
        """Resolve the layout of the project in given folder.

        Args:
            path: Project root
            pyproject: Parsed `pyproject.toml` (empty if there is none)
            fallback_name: Distribution name to use without `[project.name]`
        """
        root = pathlib.Path(path)
        dist = (pyproject.get("project") or {}).get("name") or fallback_name
        settings = (pyproject.get("tool") or {}).get("mknodes") or {}
        packages = (
            _from_settings(root, settings.get("packages"))
            or _from_build_backend(root, pyproject, dist)
            or _from_installed(dist)
            or _from_scan(root)
        )
        packages = list({p.name: p for p in packages}.values())
        packages = _sort_primary_first(packages, dist, settings.get("package"), root)
        return cls(path=root, distribution=dist, packages=packages, layout=_detect_layout(root))


def _detect_layout(root: pathlib.Path) -> Literal["src", "flat", "unknown"]:
    if (root / "src").is_dir():
        return "src"
    if any(_is_package_dir(p) for p in _iter_dirs(root)):
        return "flat"
    return "unknown"


def _sort_primary_first(
    packages: list[ImportPackage],
    dist: str,
    configured: str | None,
    root: pathlib.Path,
) -> list[ImportPackage]:
    if configured:
        match = next((p for p in packages if p.name == configured), None)
        if match is None:
            match = ImportPackage(configured, _locate(root, configured), "tool.mknodes")
        return [match, *(p for p in packages if p is not match)]
    wanted = normalize_name(dist) if dist else ""
    match = next((p for p in packages if p.name.lower() == wanted), None)
    if match is None:
        return packages
    return [match, *(p for p in packages if p is not match)]


def _locate(root: pathlib.Path, name: str, *module_roots: str) -> pathlib.Path | None:
    """Find the source of given (dotted) import name below the module roots."""
    rel = pathlib.Path(*name.split("."))
    for module_root in (*module_roots, "src", ""):
        base = root / module_root if module_root else root
        if (base / rel).is_dir():
            return base / rel
        if (file := base / rel.with_suffix(".py")).is_file():
            return file
    return None


def _from_settings(root: pathlib.Path, names: Iterable[str] | None) -> list[ImportPackage]:
    return [ImportPackage(n, _locate(root, n), "tool.mknodes") for n in names or []]


def _as_list(value: str | list[str] | None) -> list[str]:
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value)


def _from_build_backend(  # noqa: PLR0911
    root: pathlib.Path,
    pyproject: Mapping[str, Any],
    dist: str,
) -> list[ImportPackage]:
    backend = (pyproject.get("build-system") or {}).get("build-backend") or ""
    tool = pyproject.get("tool") or {}
    if backend == "uv_build":
        cfg = (tool.get("uv") or {}).get("build-backend") or {}
        names = _as_list(cfg.get("module-name")) or ([normalize_name(dist)] if dist else [])
        module_root = cfg.get("module-root", "src")
        return [ImportPackage(n, _locate(root, n, module_root), "uv_build") for n in names]
    if backend.startswith("hatchling"):
        wheel = (((tool.get("hatch") or {}).get("build") or {}).get("targets") or {}).get(
            "wheel"
        ) or {}
        paths = _as_list(wheel.get("packages"))
        return [ImportPackage(pathlib.Path(p).name, root / p, "hatch") for p in paths]
    if backend.startswith("setuptools"):
        return _from_setuptools(root, tool.get("setuptools") or {})
    if backend.startswith("flit"):
        name = ((tool.get("flit") or {}).get("module") or {}).get("name") or normalize_name(dist)
        return [ImportPackage(name, _locate(root, name), "flit")] if name else []
    if backend.startswith("poetry"):
        entries = (tool.get("poetry") or {}).get("packages") or []
        return [
            ImportPackage(e["include"], _locate(root, e["include"], e.get("from", "")), "poetry")
            for e in entries
            if isinstance(e, dict) and "include" in e and "*" not in e["include"]
        ]
    if backend == "maturin":
        cfg = tool.get("maturin") or {}
        if not (module_name := cfg.get("module-name")):
            return []
        # `pkg._native` -> the Python package is `pkg`.
        name = module_name.split(".")[0]
        return [ImportPackage(name, _locate(root, name, cfg.get("python-source", "")), "maturin")]
    return []


def _from_setuptools(root: pathlib.Path, cfg: Mapping[str, Any]) -> list[ImportPackage]:
    package_dir = (cfg.get("package-dir") or {}).get("", "")
    packages = cfg.get("packages")
    result: list[ImportPackage] = []
    if isinstance(packages, list):
        names = [p for p in packages if "." not in p]
        result = [ImportPackage(n, _locate(root, n, package_dir), "setuptools") for n in names]
    elif isinstance(packages, dict) and (find := packages.get("find")) is not None:
        include = find.get("include") or ["*"]
        exclude = find.get("exclude") or []
        for where in find.get("where") or [package_dir or "."]:
            base = root / where
            for folder in _iter_dirs(base):
                name = folder.name
                if not any(fnmatch.fnmatch(name, pat) for pat in include):
                    continue
                if any(fnmatch.fnmatch(name, pat) for pat in exclude):
                    continue
                if _is_package_dir(folder) and name not in NON_PACKAGE_DIRS:
                    result.append(ImportPackage(name, folder, "setuptools"))
    for mod in cfg.get("py-modules") or []:
        result.append(ImportPackage(mod, _locate(root, mod, package_dir), "setuptools"))
    return result


def _from_installed(dist: str) -> list[ImportPackage]:
    if not dist:
        return []
    try:
        distribution = metadata.distribution(dist)
    except metadata.PackageNotFoundError:
        return []
    if text := distribution.read_text("top_level.txt"):
        top_level = [line.strip() for line in text.splitlines() if line.strip()]
        return [ImportPackage(n, None, "installed") for n in top_level]
    names: list[str] = []
    for file in distribution.files or []:
        first = file.parts[0]
        if first.endswith((".dist-info", ".data", ".egg-info", ".pth")) or first in {
            "__pycache__",
            "..",
        }:
            continue
        if first.startswith(("__editable__", "_")) and first.endswith(".py"):
            continue
        name = first.removesuffix(".py") if len(file.parts) == 1 else first
        if (len(file.parts) > 1 or first.endswith(".py")) and name not in names:
            names.append(name)
    return [ImportPackage(n, None, "installed") for n in names]


def _iter_dirs(base: pathlib.Path) -> list[pathlib.Path]:
    if not base.is_dir():
        return []
    return sorted(
        p for p in base.iterdir() if p.is_dir() and p.name.isidentifier() and p.name[0] != "_"
    )


def _is_package_dir(path: pathlib.Path) -> bool:
    return (path / "__init__.py").is_file() and path.name not in NON_PACKAGE_DIRS


def _from_scan(root: pathlib.Path) -> list[ImportPackage]:
    src = root / "src"
    if src.is_dir():
        found = [
            ImportPackage(p.name, p, "scan")
            for p in _iter_dirs(src)
            if (p / "__init__.py").is_file() or any(p.rglob("*.py"))  # namespace packages too
        ]
        found += [
            ImportPackage(p.stem, p, "scan")
            for p in sorted(src.glob("*.py"))
            if p.stem.isidentifier() and not p.stem.startswith("_")
        ]
        return found
    return [ImportPackage(p.name, p, "scan") for p in _iter_dirs(root) if _is_package_dir(p)]


def repository_url_from_urls(urls: Mapping[str, str]) -> str | None:
    """Return the code repository URL from a `[project.urls]`-like mapping."""
    lowered = {k.lower(): v for k, v in urls.items()}
    for key in REPOSITORY_URL_KEYS:
        if url := lowered.get(key):
            return url
    return None


if __name__ == "__main__":
    from mknodes.info import pyproject

    proj = pyproject.PyProject()
    print(ProjectLayout.resolve(".", proj.data))

"""Writer producing a Sphinx project (MyST Markdown pages + generated `conf.py`).

The source folder (default `sphinx/`, the `generated_dir` setting) is fully generated:
`conf.py` (`myst-parser`, `sphinx-design`, theme `furo` unless configured), the pages
in the `myst` flavour, assets and the hand-written files of the docs folder. The nav
becomes `{toctree}` directives: the root `index.md` gets one toctree per top-level
section (with the section title as caption), section index pages get the toctree of
their section (sections without index page get a generated page). The HTML goes into
the site dir (default `site/`).

Needs the `sphinx` extra (`mknodes[sphinx]`: sphinx, myst-parser, sphinx-design, furo).
"""

import importlib.util
import pprint
import re
import shutil
import sys
from typing import TYPE_CHECKING, Any

from mknodes.site.writers.base import EngineNotFoundError, GeneratedFolder, Writer
from mknodes.site.writers.zensical import EXCLUDED_DOCS
from mknodes.utils import log


if TYPE_CHECKING:
    import pathlib

    from mknodes.build import BuildOutput, NavItem


logger = log.get_logger(__name__)

DEFAULT_SOURCE_DIR = "sphinx"
DEFAULT_SITE_DIR = "site"
CONFIG_FILE = "conf.py"
ROOT_DOC = "index.md"
STATIC_DIR = "_static"
SECTIONS_DIR = "_sections"
DEFAULT_THEME = "furo"
EXTENSIONS = ["myst_parser", "sphinx_design"]
MYST_EXTENSIONS = ["colon_fence", "deflist", "fieldlist", "html_image", "tasklist"]
SUPPRESS_WARNINGS = [
    # Code blocks in languages Pygments doesn't know (mermaid, ...) stay unhighlighted.
    "misc.highlighting_failure",
    # Pages outside the nav (and hand-written files) are fine as standalone pages.
    "toc.not_included",
    # API docs start at a configurable heading level.
    "myst.header",
    # Python-Markdown accepts these: duplicate link definitions (the first one wins),
    # footnotes without reference.
    "myst.duplicate_def",
    "ref.footnote",
]
REQUIRED_MODULES = {
    "sphinx": "sphinx",
    "myst_parser": "myst-parser",
    "sphinx_design": "sphinx-design",
}
INSTALL_HINT = (
    "Sphinx is not installed (needs {missing}). Install the `sphinx` extra "
    "(`pip install mknodes[sphinx]`), or use `mknodes generate --engine sphinx`."
)
INDEX_NAMES = ("index.md", "README.md")
HEADING_RE = re.compile(r"^#{1,6} ", re.MULTILINE)


def _docname(target: str) -> str:
    """Absolute docname of a page (`/Section/page`) for toctree entries."""
    return "/" + re.sub(r"\.md$", "", target)


def _is_index(target: str | None) -> bool:
    return target is not None and target.rsplit("/", 1)[-1] in INDEX_NAMES


def _escape_title(title: str) -> str:
    return title.replace("<", r"\<")


def toctree(entries: list[str], caption: str | None = None, *, hidden: bool = False) -> str:
    """Return a MyST `{toctree}` directive."""
    lines = ["```{toctree}", ":maxdepth: 2"]
    if caption:
        lines.append(f":caption: {caption}")
    if hidden:
        lines.append(":hidden:")
    return "\n".join([*lines, "", *entries, "```"]) + "\n"


class TocTreeWriter:
    """Turn a nav into toctrees (Sphinx has no separate nav: documents form the tree).

    Every document may appear in only one toctree (duplicates get skipped), a section
    needs a document holding its toctree: its index page, or a generated page.
    """

    def __init__(self, pages: dict[str, str]) -> None:
        self.pages = pages
        self.toctrees: dict[str, list[str]] = {}
        """Document path -> toctrees to append."""
        self.generated: dict[str, str] = {}
        """Generated section pages: path -> Markdown."""
        self.seen: set[str] = set()
        self.skipped: list[str] = []
        self.untitled: dict[str, str] = {}
        """Pages without heading -> nav title (Sphinx needs a title for the toctree)."""

    def render(self, items: list[NavItem], title: str) -> None:
        items = list(items)
        if items and not items[0].is_section and items[0].target == ROOT_DOC:
            items.pop(0)
        self.seen.add(ROOT_DOC)
        if ROOT_DOC not in self.pages:
            self.generated[ROOT_DOC] = f"# {title}\n"
        trees: list[str] = []
        loose: list[str] = []
        for item in items:
            if item.is_section:
                if loose:
                    trees.append(toctree(loose, hidden=True))
                    loose = []
                entries = self._entries(item.children, item.title)
                if entries:
                    trees.append(toctree(entries, _escape_title(item.title), hidden=True))
            elif entry := self._entry(item):
                loose.append(entry)
        if loose:
            trees.append(toctree(loose, hidden=True))
        self.toctrees.setdefault(ROOT_DOC, []).extend(trees)

    def _entries(self, items: list[NavItem], section: str) -> list[str]:
        return [entry for item in items if (entry := self._entry(item, section))]

    def _entry(self, item: NavItem, parent: str = "") -> str | None:
        title = _escape_title(item.title)
        if item.is_section:
            return self._section(item, parent)
        assert item.target
        if "://" in item.target:
            return f"{title} <{item.target}>"
        if item.target in self.seen or item.target not in self.pages:
            self.skipped.append(item.target)
            return None
        self.seen.add(item.target)
        if not HEADING_RE.search(self.pages[item.target]):
            self.untitled[item.target] = item.title
        return f"{title} <{_docname(item.target)}>"

    def _section(self, item: NavItem, parent: str) -> str | None:
        children = list(item.children)
        doc: str | None = None
        hidden = True
        if children and not children[0].is_section and _is_index(children[0].target):
            target = children[0].target
            assert target
            if target not in self.seen and target in self.pages:
                doc = target
                children.pop(0)
        if doc is None:
            doc = self._section_page(item, parent)
            hidden = False  # the generated page lists the section's pages
        self.seen.add(doc)
        if entries := self._entries(children, item.title):
            self.toctrees.setdefault(doc, []).append(toctree(entries, hidden=hidden))
        return f"{_escape_title(item.title)} <{_docname(doc)}>"

    def _section_page(self, item: NavItem, parent: str) -> str:
        slug = re.sub(r"[^\w-]+", "-", f"{parent}-{item.title}".strip("-")).strip("-").lower()
        path = f"{SECTIONS_DIR}/{slug or 'section'}.md"
        i = 1
        while path in self.generated or path in self.pages:
            i += 1
            path = f"{SECTIONS_DIR}/{slug}-{i}.md"
        self.generated[path] = f"# {item.title}\n"
        return path

    def apply(self) -> dict[str, str]:
        """Return the changed / generated pages (path -> Markdown)."""
        result = {path: f"# {title}\n\n{self.pages[path]}" for path, title in self.untitled.items()}
        for path, trees in self.toctrees.items():
            text = result.get(path) or self.generated.get(path) or self.pages.get(path, "")
            result[path] = text.rstrip("\n") + "\n\n" + "\n".join(trees)
        for path, text in self.generated.items():
            result.setdefault(path, text)
        return result


def missing_modules(theme: str | None = None) -> list[str]:
    """Return the packages needed to build which are not installed."""
    modules = dict(REQUIRED_MODULES)
    if theme and theme not in {"alabaster", "basic", "classic", "nature", "sphinxdoc"}:
        modules[theme.replace("-", "_")] = theme.replace("_", "-")
    return [pkg for mod, pkg in modules.items() if importlib.util.find_spec(mod) is None]


class SphinxWriter(Writer):
    """Write a `BuildOutput` as a Sphinx project: MyST pages + `conf.py`."""

    name = "sphinx"
    flavor = "myst"

    @property
    def source_dir(self) -> pathlib.Path:
        """The generated source folder (`generated_dir` setting, default `sphinx`)."""
        name = self.settings.generated_dir or DEFAULT_SOURCE_DIR
        return self.settings.project_dir / name

    @property
    def site_dir(self) -> pathlib.Path:
        """The HTML output folder (`site_dir` setting / site config, default `site`)."""
        name = self.settings.site_dir or self.settings.site_config.get("site_dir")
        return self.settings.project_dir / (name or DEFAULT_SITE_DIR)

    @property
    def extra_config(self) -> dict[str, Any]:
        """The `sphinx` setting."""
        return dict(self.settings.sphinx or {})

    @property
    def theme(self) -> str:
        return self.extra_config.get("theme") or DEFAULT_THEME

    def write(self, output: BuildOutput) -> pathlib.Path:
        source_dir = self.source_dir.resolve()
        protected = {self.settings.project_dir.resolve(), self.settings.resolved_docs_dir.resolve()}
        if source_dir in protected:
            msg = f"The Sphinx folder {source_dir} must not be the project or docs folder."
            raise ValueError(msg)
        folder = GeneratedFolder(source_dir, owned=True)
        self._mirror_docs(self.settings.resolved_docs_dir, folder, output, exclude=EXCLUDED_DOCS)
        tocs = TocTreeWriter(output.pages)
        tocs.render(output.nav, self._title(output))
        if tocs.skipped:
            logger.info("Not in a toctree (external or duplicate): %s", tocs.skipped)
        files = {**output.files, **tocs.apply()}
        for path, content in files.items():
            if path not in folder.written:
                folder.write(path, content)
        for path in self._static_files(output):
            folder.write(f"{STATIC_DIR}/{path}", output.assets[path])
        folder.write(CONFIG_FILE, self.render_config(output))
        removed = folder.finish()
        if output.templates:
            logger.info("Ignoring %s theme templates (Sphinx)", len(output.templates))
        logger.info(
            "Wrote %s files (%s changed, %s removed) to %s",
            len(folder.written),
            len(folder.changed),
            len(removed),
            source_dir,
        )
        self.folder = folder
        return source_dir / CONFIG_FILE

    def _static_files(self, output: BuildOutput) -> list[str]:
        paths = [*output.extra_css, *(s.path for s in output.extra_javascript)]
        return [p for p in paths if "://" not in p and p in output.assets]

    def _title(self, output: BuildOutput) -> str:
        return (
            self.settings.site_config.get("site_name")
            or output.metadata.site_name
            or self.settings.project_dir.name
        )

    def build_config(self, output: BuildOutput) -> dict[str, Any]:
        """Return the `conf.py` variables."""
        src = self.settings.site_config
        meta = output.metadata
        extra = self.extra_config
        title = self._title(output)
        config: dict[str, Any] = {"project": title}
        if author := src.get("site_author") or meta.site_author:
            config["author"] = author
        if copyright_ := src.get("copyright") or meta.copyright:
            # Sphinx adds the "©" itself.
            config["copyright"] = re.sub(r"^(Copyright\s*)?(©|&copy;)?\s*", "", copyright_)
        static = self._static_files(output)
        config |= {
            "extensions": [*EXTENSIONS, *(extra.get("extensions") or [])],
            "myst_enable_extensions": MYST_EXTENSIONS,
            "myst_heading_anchors": 6,
            "source_suffix": {".md": "markdown", ".rst": "restructuredtext"},
            "root_doc": "index",
            "exclude_patterns": ["_build", "Thumbs.db", ".DS_Store"],
            "suppress_warnings": SUPPRESS_WARNINGS,
            "html_theme": self.theme,
            "html_title": title,
            "html_static_path": [STATIC_DIR] if static else [],
            "html_css_files": [p for p in output.extra_css if p in static or "://" in p],
            "html_js_files": [
                s.path for s in output.extra_javascript if s.path in static or "://" in s.path
            ],
        }
        if site_url := src.get("site_url"):
            config["html_baseurl"] = site_url
        repo_url = src.get("repo_url") or meta.repo_url
        if repo_url and self.theme == "furo":
            config["html_theme_options"] = {"source_repository": repo_url}
        for key, value in extra.items():
            if key not in {"theme", "extensions"}:
                config[key] = value
        return config

    def render_config(self, output: BuildOutput) -> str:
        """Return `conf.py`."""
        lines = [
            "# Generated by mknodes (`--engine sphinx`). Do not edit: regenerated on every build.",
            "# Settings: `[tool.mknodes.sphinx]` in pyproject.toml.",
            "",
        ]
        for key, value in self.build_config(output).items():
            lines.append(f"{key} = {pprint.pformat(value, width=88, sort_dicts=False)}")
        return "\n".join(lines) + "\n"

    def ensure_available(self) -> None:
        if missing := missing_modules(self.theme):
            raise EngineNotFoundError(INSTALL_HINT.format(missing=", ".join(missing)))

    def build_command(
        self, *, serve: bool = False, extra_args: list[str] | None = None
    ) -> list[str]:
        self.ensure_available()
        args = list(extra_args or [])
        if "--strict" in args:
            args.remove("--strict")
            args += ["-W", "--keep-going"]  # warnings become errors
        source, site = str(self.source_dir), str(self.site_dir)
        if serve:
            if shutil.which("sphinx-autobuild") is None:
                hint = "`mknodes serve --engine sphinx` needs `sphinx-autobuild`."
                raise EngineNotFoundError(hint)
            return ["sphinx-autobuild", source, site, *args]
        return [sys.executable, "-m", "sphinx", "-b", "html", source, site, *args]
